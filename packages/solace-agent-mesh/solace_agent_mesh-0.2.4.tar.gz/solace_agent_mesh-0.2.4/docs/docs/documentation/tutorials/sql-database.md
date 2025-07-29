---
title: SQL Database Integration - sqlite3, MySQL, PostgreSQL
sidebar_position: 40
---

# SQL Database Integration

This tutorial will set up a SQL database agent in Solace Agent Mesh (SAM), which allows SAM to answer natural language queries about a sample coffee company database. This tutorial provides some sample data to set up an SQLite database, but you can use the same approach to connect to other database types, such as MySQL or PostgreSQL.

## Prerequisites

Before starting this tutorial, ensure that you have installed and configured Solace Agent Mesh:

- [Installed Solace Agent Mesh and the SAM CLI](../getting-started/installation.md)
- [Created a new Solace Agent Mesh project](../getting-started/quick-start.md)

## Installing the SQL Database Plugin

First, add the SQL Database plugin to your SAM project:

```sh
solace-agent-mesh plugin add sam_sql_database --pip -u git+https://github.com/SolaceLabs/solace-agent-mesh-core-plugins#subdirectory=sam-sql-database
```

Note that you can replace the Solace Agent Mesh CLI command with `sam` as a shortcut.

## Creating a SQL Database Agent

Next, create an agent instance based on the SQL database template:

```sh
sam add agent abc_coffee_info --copy-from sam_sql_database:sql_database
```

This command will create a new configuration file at `configs/agents/abc_coffee_info.yaml`.

## Downloading Example Data

For this tutorial, you can use a sample SQLite database for a fictional coffee company called ABC Coffee Co. 

First you should download the example data. 

You can either visit this link to download with your browser:

  https://github.com/SolaceLabs/solace-agent-mesh-core-plugins/raw/refs/heads/main/sam-sql-database/example-data/abc_coffee_co.zip

Or you can use the command line to download the ZIP file:

### Using wget
```sh
wget https://github.com/SolaceLabs/solace-agent-mesh-core-plugins/raw/refs/heads/main/sam-sql-database/example-data/abc_coffee_co.zip
```

### Using curl
```sh
curl -LO https://github.com/SolaceLabs/solace-agent-mesh-core-plugins/raw/refs/heads/main/sam-sql-database/example-data/abc_coffee_co.zip
```

After downloading the ZIP file, extract it to a directory of your choice. You can use the following command to extract the ZIP file:

```sh
unzip abc_coffee_co.zip
```

## Configuring the Agent

Now, update the agent configuration to use the SQLite database and import the CSV files.
Open the `configs/agents/abc_coffee_info.yaml` file and add the `csv_directories` option to the `action_request_processor` component configuration. This option specifies the directory where the CSV files are located.

Here's what you need to modify in the configuration file:

```yaml
# Find the component_config section for the action_request_processor and update these values:
- component_name: action_request_processor
  component_config:
    # Other configuration options (mostly specified via env vars)...
    csv_directories:
      - /path/to/your/unzipped/data
```

Ensure you replace `/path/to/your/unzipped/data` with the path where the extracted the example data is located. In this example, if you put the ZIP file in the root directory of your Solace Agent Mesh project, you can use `abc_coffee_co`.

## Setting the Environment Variables

The SQL Database agent requires that you configure several environment variables. You must create or update your `.env` file with the following variables for this tutorial:

```
ABC_COFFEE_INFO_DB_TYPE=sqlite
ABC_COFFEE_INFO_DB_NAME=abc_coffee.db
ABC_COFFEE_INFO_DB_PURPOSE="ABC Coffee Co. sales and operations database"
ABC_COFFEE_INFO_DB_DESCRIPTION="Contains information about ABC Coffee Co. products, sales, customers, employees, and store locations."
# You can leave other environment variables as unset or empty
```

SQLite stores the database in a local file and doesn't require a username or password for access. If you're using a database such as MySQL or PostgreSQL, you'll need to provide the appropriate environment variables for them.

## Running the Agent

Now, you can start Solace Agent Mesh with your new SQL database agent:

```sh
sam run -b
```
:::info
The `-b` option will rebuild the Solace Agent Mesh config files.
:::

## Interacting with the Database

After Solace Agent Mesh is running, you can interact with the ABC Coffee database through the web interface at `http://localhost:5001`.

You can ask natural language questions about the ABC Coffee Co. database, such as:

- "How many customers does ABC Coffee have?"
- "What are the top-selling products?"
- "Show me the sales by region"

Try creating reports by asking questions such as:

- "Create a report of our sales in 2024"

The SQL Database agent converts your natural language questions into SQL queries, executes them against the database, and then returns the results.

## Database Schema

The ABC Coffee Co. database contains the following tables:

- customers
- employees
- inventory
- order_history
- order_items
- orders
- product_categories
- product_specifications
- products
- sales_call_logs
- support_ticket_comments
- support_tickets

When the agent initializes, it learns the schemas for each of the mentioned tables.

## Conclusion

You've successfully set up a SQL Database agent in Solace Agent Mesh that can answer natural language queries about the ABC Coffee Co. database. The same approach can be applied to connect to other database types, such as MySQL or PostgreSQL - you only need to adjust the configuration and environment variables accordingly.

For more information about the SQL Database plugin, see [plugin README](https://github.com/SolaceLabs/solace-agent-mesh-core-plugins/blob/main/sam-sql-database/README.md).
