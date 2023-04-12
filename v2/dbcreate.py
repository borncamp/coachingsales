import os
import pyodbc
import json
import time

from azure.identity import AzureCliCredential
from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.sql import SqlManagementClient
from azure.mgmt.sql.models import (
    Sku, Server, ServerForCreate, FirewallRule, FirewallRuleForCreate, Database, DatabaseForCreate,
    CreateMode
)
from msrestazure.azure_exceptions import CloudError

# Load Azure configuration from a JSON file
with open('azure_config.json', 'r') as f:
    azure_config = json.load(f)

# Get the admin password from a shell variable
admin_password = os.environ.get('ADMIN_PASSWORD')

if admin_password is None:
    raise ValueError("Please set the ADMIN_PASSWORD environment variable.")

# Initialize Azure credentials
credential = AzureCliCredential()

# Initialize Azure Resource Management and SQL Management clients
resource_client = ResourceManagementClient(credential, azure_config['subscription_id'])
sql_client = SqlManagementClient(credential, azure_config['subscription_id'])

# Define variables for the Azure SQL Server and Database
server_name = azure_config['server_name']
admin_login = azure_config['admin_login']
database_name = azure_config['database_name']
resource_group_name = azure_config['resource_group_name']
location = azure_config['location']

# Create a resource group
resource_group_params = {'location': location}
resource_group = resource_client.resource_groups.create_or_update(
    resource_group_name, resource_group_params)

print(f"Resource group '{resource_group.name}' created successfully.")

# Create an Azure SQL Server
server_params = ServerForCreate(
    administrator_login=admin_login,
    administrator_login_password=admin_password,
    version='12.0',
    tags={
        'application': 'LinkedIn Bot'
    },
    location=location
)
server = sql_client.servers.create_or_update(
    resource_group_name, server_name, server_params)

print(f"Azure SQL Server '{server.name}' created successfully.")

# Define a client IP address for a firewall rule
client_ip_address = '0.0.0.0'

# Create a firewall rule to allow connections from the client IP address
firewall_rule_params = FirewallRuleForCreate(
    start_ip_address=client_ip_address,
    end_ip_address=client_ip_address,
    name='AllowClientIP',
    description='Allow connections from client IP address'
)
firewall_rule = sql_client.firewall_rules.create_or_update(
    resource_group_name, server_name, firewall_rule_params, firewall_rule_name='AllowClientIP')

print(f"Firewall rule '{firewall_rule.name}' created successfully.")

# Create an Azure SQL Database
database_params = DatabaseForCreate(
    collation='SQL_Latin1_General_CP1_CI_AS',
    edition='Basic',
    location=location,
    max_size_bytes=268435456000,
    requested_service_objective_name='Basic',
    create_mode=CreateMode.default,
    tags={
        'application': 'LinkedIn Bot'
    }
)
database = sql_client.databases.create_or_update(
    resource_group_name, server_name, database_name, database_params)

print(f"Azure SQL Database '{database.name}' created successfully.")

