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

# Loop through new messages and respond with a follow-up message
while True:
    conversations = client.get_conversations()
    for conversation in conversations:
        # Ignore messages that are not from the "conversation opener" script
        if conversation['with']['firstName'] != 'Connection' or conversation['with']['lastName'] != 'Requestor':
            continue
        # Ignore messages that are not from the most recent message sent by the "conversation opener" script
        messages = conversation['messages']
        if not messages:
            continue
        latest_message = messages[-1]
        if latest_message['from'] != 'INBOX':
            continue
        # Ignore messages that are not replies to the message sent by the "conversation opener" script
        parent_message_id = latest_message['parentUrn'].split(':')[-1]
        parent_message = client.get_message(parent_message_id)
        if parent_message['created_at'] != messages[-2]['createdAt']:
            continue
        # Ignore messages that do not contain the specified trigger phrase
        trigger_phrase = "willing to say more"
        message_text = latest_message['attributedBody']['text']
        if trigger_phrase not in message_text:
            continue
        # Send the follow-up message
        profile_id = conversation['with']['entityUrn'].split(':')[-1]
        message = "Thanks for your response! Would you be willing to say more about what you find most rewarding and most challenging in your role at your company?"
        client.send_message(profile_id, message)
        print(f"Sent follow-up message to {conversation['with']['firstName']} {conversation['with']['lastName']}")
        
    # Wait for 10 seconds before checking again
    time.sleep(10)

