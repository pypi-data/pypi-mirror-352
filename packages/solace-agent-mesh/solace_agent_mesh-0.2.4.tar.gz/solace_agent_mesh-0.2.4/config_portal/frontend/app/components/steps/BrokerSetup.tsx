import { useEffect, useState, useCallback } from 'react';
import FormField from '../ui/FormField';
import Input from '../ui/Input';
import Select from '../ui/Select';
import Button from '../ui/Button';
import { InfoBox, WarningBox, StatusBox } from '../ui/InfoBoxes';
import ConfirmationModal from '../ui/ConfirmationModal';

type BrokerSetupProps = {
  data: { 
    broker_type: string;
    broker_url: string;
    broker_vpn: string;
    broker_username: string;
    broker_password: string;
    container_engine?: string;
    container_started?: boolean;
    [key: string]: any 
  };
  updateData: (data: Record<string, any>) => void;
  onNext: () => void;
  onPrevious: () => void;
};

const brokerOptions = [
  { value: 'solace', label: 'Existing Solace Pub/Sub+ broker' },
  { value: 'container', label: 'New local Solace PubSub+ broker container' },
  { value: 'dev_mode', label: 'Dev mode (simplified setup)' },
];

const containerEngineOptions = [
  { value: 'podman', label: 'Podman' },
  { value: 'docker', label: 'Docker' },
];

export default function BrokerSetup({ data, updateData, onNext, onPrevious }: Readonly<BrokerSetupProps>) {
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [isRunningContainer, setIsRunningContainer] = useState(false);
  const [isTestingConnection, setIsTestingConnection] = useState<boolean>(false);
  const [connectionTestMessage, setConnectionTestMessage] = useState<string | null>(null);
  const [showConnectionErrorDialog, setShowConnectionErrorDialog] = useState<boolean>(false);
  const [containerStatus, setContainerStatus] = useState<{
    isRunning: boolean;
    success: boolean;
    message: string;
  }>({
    isRunning: false,
    success: data.container_started === true,
    message: data.container_started ? 'Container already started successfully' : '',
  });

  useEffect(() => {
    if (!data.container_engine && data.broker_type === 'container') {
      updateData({ container_engine: 'podman' });
    }
    if (data.container_engine && data.broker_type !== 'container') {
      updateData({ container_engine: '' });
    }
    
    // Set dev_mode to false if it's not the selected broker type
    if (data.broker_type !== 'dev_mode') {
      updateData({ dev_mode: false });
    } else if (data.broker_type === 'dev_mode') {
      updateData({ dev_mode: true });
    }
    
  }, [data.broker_type, updateData]);

  useEffect(() => {
    if (data.broker_type !== 'solace') {
      setConnectionTestMessage(null);
      setShowConnectionErrorDialog(false);
      setIsTestingConnection(false);
    }
  }, [data.broker_type]);
  
  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    updateData({ [e.target.name]: e.target.value });
  };
  
  const validateForm = () => {
    const newErrors: Record<string, string> = {};
    let isValid = true;
    
    // Validation for existing broker
    if (brokerType === 'solace') {
      if (!data.broker_url) {
        newErrors.broker_url = 'Broker URL is required';
        isValid = false;
      }
      if (!data.broker_vpn) {
        newErrors.broker_vpn = 'VPN name is required';
        isValid = false;
      }
      if (!data.broker_username) {
        newErrors.broker_username = 'Username is required';
        isValid = false;
      }
      if (!data.broker_password) {
        newErrors.broker_password = 'Password is required';
        isValid = false;
      }
    }
    
    // Validation for container - ensure container has been successfully started
    if (brokerType === 'container' && !containerStatus.success) {
      newErrors.container = 'You must successfully run the container before proceeding';
      isValid = false;
    }
    
    setErrors(newErrors);
    return isValid;
  };
  
  const handleRunContainer = async () => {
    setIsRunningContainer(true);
    setContainerStatus({
      isRunning: true,
      success: false,
      message: 'Starting container...',
    });
    
    try {
      const response = await fetch('api/runcontainer', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          container_engine: data.container_engine
        }),
      });
      
      const result = await response.json();
      
      if (result.status === 'success') {
        setContainerStatus({
          isRunning: false,
          success: true,
          message: result.message ?? 'Container started successfully!'
        });
        // Store the container status in the data for persistence
        updateData({ 
          container_engine: data.container_engine,
          container_started: true 
        });
      } else {
        setContainerStatus({
          isRunning: false,
          success: false,
          message: result.message ?? 'Failed to start container. Please try again.'
        });
        // Clear the container_started flag on failure
        updateData({ container_started: false });
      }
    } catch (error) {
      setContainerStatus({
        isRunning: false,
        success: false,
        message: error instanceof Error ? error.message : 'An unexpected error occurred'
      });
      // Clear the container_started flag on error
      updateData({ container_started: false });
    } finally {
      setIsRunningContainer(false);
    }
  };

  const handleTestConnection = async (): Promise<boolean> => {
    setIsTestingConnection(true);
    setConnectionTestMessage(null);
    setShowConnectionErrorDialog(false);

    try {
      const response = await fetch('/api/test_broker_connection', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          broker_url: data.broker_url,
          broker_vpn: data.broker_vpn,
          broker_username: data.broker_username,
          broker_password: data.broker_password,
        }),
      });
      const result = await response.json();

      if (result.status === 'success') {
        setIsTestingConnection(false);
          onNext();
        return true;
      } else {
        setConnectionTestMessage(result.message ?? 'Connection failed.');
        setShowConnectionErrorDialog(true);
        setIsTestingConnection(false);
        return false;
      }
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'An unexpected network error occurred.';
      setConnectionTestMessage(errorMessage);
      setShowConnectionErrorDialog(true);
      setIsTestingConnection(false);
      return false;
    }
  };
  
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (validateForm()) {
      if (data.broker_type === 'solace') {
        // Always attempt test connection on submit for 'solace' type
        await handleTestConnection();
      } else {
        onNext();
      }
    }
  };
  
  const brokerType = data.broker_type;
  
  // Show broker connection details default option
  const showBrokerDetails = brokerType === 'solace';
  const showContainerDetails = brokerType === 'container';
  
  const getStatusBoxVariant = () => {
    if (containerStatus.isRunning) return 'loading';
    if (containerStatus.success) return 'success';
    return 'error';
  };
  
  const renderButtonContent = () => {
    if (isRunningContainer) {
      return (
        <>
          <svg className="animate-spin h-4 w-4 mr-2" viewBox="0 0 24 24">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none"></circle>
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          Starting Container...
        </>
      );
    }
    
    if (containerStatus.success) {
      return (
        <>
          <svg className="h-4 w-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
          </svg>
          Container Running
        </>
      );
    }
    
    return (
      <>
        <svg className="h-4 w-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
        </svg>
        Download and Run Container
      </>
    );
  };
  
  return (
    <>
      <form onSubmit={handleSubmit}>
        <div className="space-y-6">
        
          <FormField
          label="Broker Type" 
          htmlFor="broker_type"
          required
        >
          <Select
            id="broker_type"
            name="broker_type"
            options={brokerOptions}
            value={brokerType}
            onChange={handleChange}
            disabled={containerStatus.success && data.broker_type==='container'}
          />
        </FormField>
        
        {showBrokerDetails && (
          <div className="space-y-4 p-4 border border-gray-200 rounded-md">
            <InfoBox className="mb-4">
              Connect to an existing Solace PubSub+ broker running locally or in the cloud. You will need your broker credentials.
            </InfoBox>
            
            <FormField 
              label="Broker URL" 
              htmlFor="broker_url"
              error={errors.broker_url}
              required
            >
              <Input
                id="broker_url"
                name="broker_url"
                value={data.broker_url || ''}
                onChange={handleChange}
                placeholder="ws://localhost:8008"
              />
            </FormField>
            
            <FormField 
              label="VPN Name" 
              htmlFor="broker_vpn"
              error={errors.broker_vpn}
              required
            >
              <Input
                id="broker_vpn"
                name="broker_vpn"
                value={data.broker_vpn || ''}
                onChange={handleChange}
                placeholder="default"
              />
            </FormField>
            
            <FormField 
              label="Username" 
              htmlFor="broker_username"
              error={errors.broker_username}
              required
            >
              <Input
                id="broker_username"
                name="broker_username"
                value={data.broker_username || ''}
                onChange={handleChange}
                placeholder="default"
              />
            </FormField>
            
            <FormField 
              label="Password" 
              htmlFor="broker_password"
              error={errors.broker_password}
              required
            >
              <Input
                id="broker_password"
                name="broker_password"
                type="password"
                value={data.broker_password || ''}
                onChange={handleChange}
                placeholder="Enter password"
              />
            </FormField>
          </div>
        )}
        
      {showContainerDetails && (
          <div className="space-y-4 p-4 border border-gray-200 rounded-md">
            <InfoBox className="mb-4">
              This option will download and run a local Solace PubSub+ broker container on your machine using Docker or Podman.
              You need to have Docker or Podman installed on your system.
            </InfoBox>
            
            <FormField 
              label="Container Engine" 
              htmlFor="container_engine"
              helpText="Select the container engine installed on your system"
              required
            >
              <Select
                id="container_engine"
                name="container_engine"
                options={containerEngineOptions}
                value={data.container_engine ?? ''}
                onChange={handleChange}
                disabled={containerStatus.isRunning || containerStatus.success}
              />
            </FormField>
            
            {errors.container && (
              <div className="text-sm text-red-600 mt-1 bg-red-50 p-2 border-l-4 border-red-500">
                {errors.container}
              </div>
            )}
            
            {/* Display container status message using StatusBox component */}
            {containerStatus.message && (
              <StatusBox variant={getStatusBoxVariant()}>
                {containerStatus.message}
              </StatusBox>
            )}
            
            <div className="relative">
              <div className="flex flex-col">
                <Button 
                  onClick={handleRunContainer}
                  disabled={isRunningContainer || containerStatus.success}
                  variant="primary"
                  type="button"
                  className="flex items-center justify-center gap-2"
                >
                  {renderButtonContent()}
                </Button>
                
                {containerStatus.success && (
                  <div className="mt-2 flex items-center text-sm text-green-600">
                    <svg className="h-4 w-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    Container is running. You may proceed to the next step.
                  </div>
                )}
                
                {!containerStatus.success && !isRunningContainer && !containerStatus.message && (
                  <div className="mt-2 flex items-center text-sm text-blue-600">
                    <svg className="h-4 w-4 mr-1" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2} strokeLinecap="round" strokeLinejoin="round">
                      <circle cx="12" cy="12" r="10" />
                      <line x1="12" y1="16" x2="12" y2="12" />
                      <line x1="12" y1="8" x2="12" y2="8" />
                    </svg>
                    You must start the container before proceeding to the next step
                  </div>
                )}
              </div>
            </div>
          </div>
        )}
        
        {brokerType === 'dev_mode' && (
            <WarningBox>
            <strong>Warning:</strong> Dev mode runs everything in a single process and is not recommended for production use.
            </WarningBox>
        )}
      </div>
      
      <div className="mt-8 flex justify-end space-x-4">
        <Button 
          onClick={onPrevious}
          variant="outline"
          type="button"
        >
          Previous
        </Button>
        
        <Button
          type='submit'
          disabled={isTestingConnection || isRunningContainer || (brokerType === 'container' && !containerStatus.success)}
          variant={brokerType === 'container' && !containerStatus.success ? "secondary" : "primary"}
        >
          {brokerType === 'container' && !containerStatus.success && !isRunningContainer && (
            <span className="flex items-center">
              <svg className="h-4 w-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
              </svg>
              Run Container First
            </span>
          )}
          {!(brokerType === 'container' && !containerStatus.success && !isRunningContainer) && "Next"}
        </Button>
      </div>
      </form>

      {/* Loading indicator for connection test */}
      {isTestingConnection && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-md w-full text-center">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Testing Broker Connection</h3>
            <div className="flex justify-center mb-4">
              <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-solace-green"></div>
            </div>
            <p>Please wait while we test your broker configuration...</p>
          </div>
        </div>
      )}

      {showConnectionErrorDialog && (
        <ConfirmationModal
          title="Connection Test Failed"
          message={`We couldn't connect to your Solace broker: ${connectionTestMessage || 'Unknown error.'}\n\nPlease check your Broker URL, VPN Name, Username, and Password.\n\nDo you want to skip this check and continue anyway?`}
          onConfirm={() => {
            setShowConnectionErrorDialog(false);
            onNext();
          }}
          onCancel={() => {
            setShowConnectionErrorDialog(false);
          }}
        />
      )}
    </>
  );
}