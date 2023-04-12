import pyodbc
import os
import time
from linkedin_api import Linkedin

# Set up connection to the Azure SQL database
server = os.environ['SQL_SERVER']
database = os.environ['SQL_DATABASE']
username = os.environ['SQL_USERNAME']
password = os.environ['SQL_PASSWORD']
driver = '{ODBC Driver 17 for SQL Server}'
cnxn = pyodbc.connect(f'DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password}')
cursor = cnxn.cursor()

# Log in to LinkedIn account
email = os.environ['LINKEDIN_EMAIL']
password = os.environ['LINKEDIN_PASSWORD']
api = Linkedin(email, password)

# Define function to send a message
def send_message(recipient_id, message):
    api.messaging.post_message({
        'keyVersion': 'LEGACY_INBOX',
        'conversationId': recipient_id,
        'messageCreate': {
            'eventCreate': {
                'value': message
            }
        }
    })

# Define function to get new message recipients from database
def get_new_message_recipients():
    cursor.execute('SELECT DISTINCT recipient_id FROM message_log WHERE script_name = "say more" AND response_text IS NOT NULL AND coaching_opener_sent_at IS NULL')
    return [row.recipient_id for row in cursor.fetchall()]

# Define function to update database with coaching opener message send time
def update_coaching_opener_sent_at(recipient_id):
    cursor.execute(f'UPDATE message_log SET coaching_opener_sent_at = GETUTCDATE() WHERE recipient_id = "{recipient_id}" AND script_name = "say more"')
    cnxn.commit()

# Define main function
def main():
    recipients = get_new_message_recipients()
    if not recipients:
        print('No new message recipients')
        return
    for recipient in recipients:
        try:
            send_message(recipient, "Hi there, I work with people in roles like yours to solve those kinds of challenges and create more opportunities for what they find rewarding. Would you be interested in a 15 minute call to learn more?")
            update_coaching_opener_sent_at(recipient)
            print(f'Coaching opener message sent to recipient {recipient}')
            time.sleep(5)
        except Exception as e:
            print(f'Error sending message to recipient {recipient}: {str(e)}')

if __name__ == '__main__':
    main()

