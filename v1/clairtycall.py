import os
import pyodbc
import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException


# Set up database connection
server = '<server-name>.database.windows.net'
database = '<database-name>'
username = '<username>'
password = '<password>'
driver= '{ODBC Driver 17 for SQL Server}'
cnxn = pyodbc.connect(f'DRIVER={driver};SERVER={server};PORT=1433;DATABASE={database};UID={username};PWD={password}')
cursor = cnxn.cursor()


# Set up LinkedIn login credentials
username = "<linkedin-username>"
password = "<linkedin-password>"


# Set up Chrome driver options
chrome_options = Options()
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')
chrome_options.add_argument('--disable-gpu')
chrome_options.add_argument('--headless')


# Set up Chrome driver
driver = webdriver.Chrome(options=chrome_options)


# Log in to LinkedIn
driver.get('https://www.linkedin.com/login')
driver.find_element_by_id('username').send_keys(username)
driver.find_element_by_id('password').send_keys(password)
driver.find_element_by_xpath("//button[contains(.,'Sign in')]").click()


# Set up message to send
message = "Hey! Just following up on our conversation. If you're interested, I'd love to hop on a quick 15 minute call to learn more about what you're looking for in your career. Here's a link to my Calendly: https://calendly.com/bborncamp/clarity-call"


# Check for new messages in database
while True:
    cursor.execute("SELECT * FROM CoachingOpener WHERE Response IS NOT NULL AND FollowUpSent IS NULL")
    rows = cursor.fetchall()
    if rows:
        for row in rows:
            message_to = row[0]
            # Send message to user
            driver.get('https://www.linkedin.com/messaging/compose/')
            driver.find_element_by_xpath('//span[text()="Search for people"]').click()
            search_bar = driver.find_element_by_xpath('//input[@placeholder="Search"]')
            search_bar.send_keys(message_to)
            search_bar.send_keys(Keys.RETURN)
            time.sleep(2)
            try:
                driver.find_element_by_xpath("//span[contains(.,'Connect')]").click()
            except NoSuchElementException:
                pass
            time.sleep(2)
            try:
                driver.find_element_by_xpath("//span[contains(.,'Add a note')]").click()
                note = driver.find_element_by_xpath("//textarea[@name='message']")
                actions = ActionChains(driver)
                actions.move_to_element(note)
                actions.click()
                actions.send_keys(message)
                actions.perform()
                time.sleep(2)
                driver.find_element_by_xpath("//span[text()='Send']").click()
                cursor.execute(f"UPDATE CoachingOpener SET FollowUpSent=1 WHERE Person='{message_to}'")
                cursor.commit()
            except NoSuchElementException:
                pass
    else:
        time.sleep(60)

# Close database connection and Chrome driver
cursor.close()
cnxn.close()
driver.quit()

