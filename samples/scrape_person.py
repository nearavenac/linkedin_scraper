import os
from dotenv import load_dotenv
from linkedin_scraper import Person, actions
from selenium import webdriver
from selenium.webdriver.chrome.service import Service

load_dotenv()

CHROMEDRIVER_PATH = os.getenv("CHROMEDRIVER_PATH")
service = Service(executable_path=CHROMEDRIVER_PATH)
driver = webdriver.Chrome(service=service)

email = os.getenv("LINKEDIN_USER")
password = os.getenv("LINKEDIN_PASSWORD")
profile_url = "https://www.linkedin.com/in/nicolas-aravena-cancino/"
actions.login(driver, email, password, redirect_url=profile_url)
person = Person(profile_url, driver=driver)

data = person.to_dict()
print(data)
