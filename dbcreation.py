import pyodbc
import os

# Azure SQL Database server configuration
server_name = '<server_name>.database.windows.net'
database_name = 'CoachSalesDB'
admin_login = '<admin_login>'
admin_password = '<admin_password>'

# Create Azure SQL Database server
os.system(f'az sql server create --name {server_name} --resource-group MyResourceGroup --location eastus --admin-user {admin_login} --admin-password {admin_password} --enable-public-network true')

# Configure firewall rule to allow access to the database
os.system(f'az sql server firewall-rule create --resource-group MyResourceGroup --server {server_name} --name AllowAllIps --start-ip-address 0.0.0.0 --end-ip-address 255.255.255.255')

# Create Azure SQL Database
os.system(f'az sql db create --name {database_name} --resource-group MyResourceGroup --server {server_name} --service-objective S0')

# Connect to Azure SQL Database
driver= '{ODBC Driver 17 for SQL Server}'
server = server_name
database = database_name
username = admin_login
password = admin_password
cnxn = pyodbc.connect(f'DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password}')

# Create ConnectionRequestor table
cursor = cnxn.cursor()
cursor.execute('''
    CREATE TABLE ConnectionRequestor (
        Id INT NOT NULL IDENTITY(1,1) PRIMARY KEY,
        FirstName NVARCHAR(50) NOT NULL,
        LastName NVARCHAR(50) NOT NULL,
        Email NVARCHAR(50) NOT NULL,
        Phone NVARCHAR(50) NOT NULL,
        Timestamp DATETIME NOT NULL DEFAULT GETDATE()
    );
''')
cursor.commit()

# Create ConversationOpener table
cursor.execute('''
    CREATE TABLE ConversationOpener (
        Id INT NOT NULL IDENTITY(1,1) PRIMARY KEY,
        Email NVARCHAR(50) NOT NULL,
        Message NVARCHAR(500) NOT NULL,
        Timestamp DATETIME NOT NULL DEFAULT GETDATE()
    );
''')
cursor.commit()

# Create SayMore table
cursor.execute('''
    CREATE TABLE SayMore (
        Id INT NOT NULL IDENTITY(1,1) PRIMARY KEY,
        Email NVARCHAR(50) NOT NULL,
        Message NVARCHAR(500) NOT NULL,
        Timestamp DATETIME NOT NULL DEFAULT GETDATE()
    );
''')
cursor.commit()

# Create CoachingOpener table
cursor.execute('''
    CREATE TABLE CoachingOpener (
        Id INT NOT NULL IDENTITY(1,1) PRIMARY KEY,
        Email NVARCHAR(50) NOT NULL,
        Message NVARCHAR(500) NOT NULL,
        Timestamp DATETIME NOT NULL DEFAULT GETDATE()
    );
''')
cursor.commit()

# Create ClarityCallOffer table
cursor.execute('''
    CREATE TABLE ClarityCallOffer (
        Id INT NOT NULL IDENTITY(1,1) PRIMARY KEY,
        Email NVARCHAR(50) NOT NULL,
        Timestamp DATETIME NOT NULL DEFAULT GETDATE()
    );
''')
cursor.commit()

print('All tables created successfully.')

