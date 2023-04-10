import os
import re
import pyodbc
import time
from datetime import datetime
from linkedin_api import Linkedin

# Initialize the LinkedIn API client
client = Linkedin(
    os.environ['LINKEDIN_EMAIL'],
    os.environ['LINKEDIN_PASSWORD'],
    refresh_cookies=True
)

# Define the list of keywords to look for in the position field
keywords = [
    'software', 'developer', 'engineer', 'programmer', 'coding', 'devops',
    'systems', 'network', 'information technology', 'it', 'data', 'analytics',
    'database', 'web', 'frontend', 'backend', 'fullstack', 'cloud', 'cybersecurity'
]

# Connect to the Azure SQL Database
server = '<your_server>.database.windows.net'
database = '<your_database>'
username = '<your_username>'
password = '<your_password>'
driver = '{ODBC Driver 17 for SQL Server}'
cnxn = pyodbc.connect(f'DRIVER={driver};SERVER={server};PORT=1433;DATABASE={database};UID={username};PWD={password}')
cursor = cnxn.cursor()

# Create a table to store the connection requests
cursor.execute('''CREATE TABLE IF NOT EXISTS connection_requests
             (id INT IDENTITY(1,1) PRIMARY KEY,
              timestamp DATETIME2 NOT NULL,
              name NVARCHAR(255) NOT NULL,
              position NVARCHAR(255) NOT NULL,
              message NVARCHAR(MAX) NOT NULL)''')
cnxn.commit()

# Loop through each connection and check their connections for new profiles to add
while True:
    connections = client.get_connections()
    for connection in connections:
        profile_id = connection['entityUrn'].split(':')[-1]
        profile = client.get_profile(profile_id)
        name = profile['firstName'] + ' ' + profile['lastName']
        positions = [e['title'] for e in profile['positions']]
        for position in positions:
            if any(keyword in position.lower() for keyword in keywords):
                message = f"Hi {profile['firstName']}, I saw your profile and noticed that you work in {position}. I'd like to connect with you and learn more about your work."
                print(f"Sending connection request to {name} ({position})")
                
                # Log the connection request in the database
                now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                cursor.execute("INSERT INTO connection_requests (timestamp, name, position, message) VALUES (?, ?, ?, ?)",
                  (now, name, position, message))
                cnxn.commit()
                
                # Send the connection request using the LinkedIn API
                client.send_invitation(profile_id=profile_id, message=message)
                
                # Wait a few seconds to avoid triggering LinkedIn's rate limits
                time.sleep(5)
    # Wait for 10 minutes before checking again
    time.sleep(600)

