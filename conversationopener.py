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

# Connect to the Azure SQL Database
server = '<your_server>.database.windows.net'
database = '<your_database>'
username = '<your_username>'
password = '<your_password>'
driver = '{ODBC Driver 17 for SQL Server}'
cnxn = pyodbc.connect(f'DRIVER={driver};SERVER={server};PORT=1433;DATABASE={database};UID={username};PWD={password}')
cursor = cnxn.cursor()

# Loop through each new connection and send a follow-up message
while True:
    cursor.execute("SELECT * FROM connection_requests WHERE follow_up_sent IS NULL")
    rows = cursor.fetchall()
    for row in rows:
        name = row[2]
        company = row[4]
        message = f"Hi {name}, I hope you're doing well! I wanted to follow up and see how you're feeling at {company}."
        profile_id = client.search_people(name, search_1st_connections_only=True)[0]['entityUrn'].split(':')[-1]
        client.send_message(profile_id, message)
        print(f"Sent follow-up message to {name} at {company}")
        
        # Mark the follow-up message as sent in the database
        cursor.execute("UPDATE connection_requests SET follow_up_sent = ? WHERE id = ?", (datetime.now(), row[0]))
        cnxn.commit()
        
        # Wait a few seconds to avoid triggering LinkedIn's rate limits
        time.sleep(5)
        
    # Wait for 10 minutes before checking again
    time.sleep(600)

