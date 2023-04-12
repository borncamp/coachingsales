import linkedin_api
import re
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

# Initialize the LinkedIn API client
api = linkedin_api.Linkedin('YOUR_LINKEDIN_EMAIL', 'YOUR_LINKEDIN_PASSWORD')

# List of job titles related to software engineering or IT
it_jobs = ['software', 'engineer', 'developer', 'programmer', 'architect', 'database', 'security', 'network', 'devops', 'cloud', 'data', 'web', 'mobile', 'frontend', 'backend', 'fullstack', 'analyst', 'consultant']

# Get a list of your existing connections
connections = api.get_network(depth=1)

# Iterate over each connection
for connection in connections:
    # Get the person's profile
    person = api.get_profile(connection['public_id'])
    
    # Check if you have already sent a connection request to this person
    if not connection['pending_invitation']:
        # Check if the person works in software engineering or IT related jobs
        has_it_job = False
        for position in person.get('positions', []):
            job_title = position.get('title', '').lower()
            for it_job in it_jobs:
                if it_job in job_title:
                    has_it_job = True
                    break
            if has_it_job:
                break
        
        if has_it_job:
            # Extract the person's recent employment history
            recent_job = person['positions'][0]['title']
            recent_company = person['positions'][0]['company']

            # Clean up the recent employment history
            recent_job = re.sub('[^A-Za-z]+', '', recent_job)
            recent_company = re.sub('[^A-Za-z]+', '', recent_company)

            # Personalized introduction message
            intro_message = f"Hi, I noticed that you work as a {recent_job} at {recent_company}. I'd love to connect and learn more about your work!"

            # Open LinkedIn in a browser
            driver = webdriver.Chrome()
            driver.get('https://www.linkedin.com')

            # Log in to LinkedIn
            email = driver.find_element_by_name('session_key')
            password = driver.find_element_by_name('session_password')
            email.send_keys('YOUR_LINKEDIN_EMAIL')
            password.send_keys('YOUR_LINKEDIN_PASSWORD')
            password.submit()

            # Navigate to the person's profile
            driver.get(f'https://www.linkedin.com/in/{person["public_id"]}')

            # Click the "Connect" button
            connect_button = driver.find_element_by_class_name('pv-s-profile-actions__overflow-toggle')
            connect_button.click()
            driver.find_element_by_class_name('mr1').click()

            # Add personalized message
            message_box = driver.find_element_by_id('custom-message')
            message_box.send_keys(intro_message)

            # Send connection request
            send_button = driver.find_element_by_class_name('ml1')
            send_button.click()

            # Close the browser
            driver.quit()

