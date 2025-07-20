import os
import json
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from dotenv import load_dotenv
from linkedin_scraper import Person, actions
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from linkedin_scraper.utils import instance_to_dict

load_dotenv()

CHROMEDRIVER_PATH = os.getenv("CHROMEDRIVER_PATH")
service = Service(executable_path=CHROMEDRIVER_PATH)
driver = webdriver.Chrome(service=service)

email = os.getenv("LINKEDIN_USER")
password = os.getenv("LINKEDIN_PASSWORD")
actions.login(driver, email, password) # if email and password isnt given, it'll prompt in terminal
person = Person("https://www.linkedin.com/in/nicolas-aravena-cancino/", driver=driver)

data = instance_to_dict(person)
print(json.dumps(data, indent=2, ensure_ascii=False))
