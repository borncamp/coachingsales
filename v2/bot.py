import time
import pyodbc
import datetime
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

class LinkedInBot:
    def __init__(self, email, password):
        self.email = email
        self.password = password
        self.driver = webdriver.Chrome()

        # Set up a connection to your Azure SQL database
        server = 'your_server_name.database.windows.net'
        database = 'your_database_name'
        username = 'your_username'
        password = 'your_password'
        driver= '{ODBC Driver 17 for SQL Server}'

        self.cnxn = pyodbc.connect(f'DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password}')
        self.cursor = self.cnxn.cursor()

    def login(self):
        self.driver.get("https://www.linkedin.com/login")
        email_input = self.driver.find_element_by_name("session_key")
        email_input.send_keys(self.email)
        password_input = self.driver.find_element_by_name("session_password")
        password_input.send_keys(self.password)
        password_input.submit()
        time.sleep(5)

    def send_message(self, profile_url, message):
        self.driver.get(profile_url)
        message_button = self.driver.find_element_by_xpath("//span[text()='Message']")
        message_button.click()
        time.sleep(2)
        message_input = self.driver.find_element_by_xpath("//div[contains(@class, 'msg-form__contenteditable t-14 t-black--light t-normal flex-grow-1')]")
        message_input.send_keys(message)
        message_input.send_keys(Keys.RETURN)
        time.sleep(5)

        # Log the message action to the database
        self.log_action(profile_url, 'message', message)

    def send_connection_request(self, profile_url):
        self.driver.get(profile_url)
        connect_button = self.driver.find_element_by_xpath("//button[text()='Connect']")
        connect_button.click()
        time.sleep(2)
        add_note_button = self.driver.find_element_by_xpath("//span[text()='Add a note']")
        add_note_button.click()
        time.sleep(2)
        message_input = self.driver.find_element_by_xpath("//textarea[contains(@class, 'send-invite__custom-message')]")
        message_input.send_keys("Hi, I'd like to connect with you on LinkedIn.")
        send_button = self.driver.find_element_by_xpath("//button[text()='Send']")
        send_button.click()
        time.sleep(5)

        # Log the connection request action to the database
        self.log_action(profile_url, 'connection_request')

    def log_action(self, profile_url, action_type, message=None):
        timestamp = datetime.datetime.now()
        query = f"INSERT INTO actions (profile_url, action_type, message, timestamp) VALUES ('{profile_url}', '{action_type}', '{message}', '{timestamp}')"
        self.cursor.execute(query)
        self.cnxn.commit()

    def logout(self):
        self.driver.quit()
        self.cnxn.close()

if __name__ == '__main__':
    bot = LinkedInBot('your_email@example.com', 'your_password')
    bot.login()
    bot.send_message('https://www.linkedin.com/in/janedoe/', 'Hi Jane, how are you doing?')
    bot.send_connection_request('https://www.linkedin.com/in/janedoe/')
    bot.logout()

