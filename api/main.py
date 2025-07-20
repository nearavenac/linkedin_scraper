import os
from dotenv import load_dotenv
from fastapi import FastAPI, Query, HTTPException
from linkedin_scraper import Person, actions, utils
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

load_dotenv()
app = FastAPI()

CHROMEDRIVER_PATH = os.getenv("CHROMEDRIVER_PATH")
LINKEDIN_USER = os.getenv("LINKEDIN_USER")
LINKEDIN_PASSWORD = os.getenv("LINKEDIN_PASSWORD")

def get_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    service = Service(executable_path=CHROMEDRIVER_PATH)
    return webdriver.Chrome(service=service, options=chrome_options)

@app.get("/scrape_person")
def scrape_person(profile_url: str = Query(..., description="LinkedIn profile URL")):
    if not CHROMEDRIVER_PATH or not LINKEDIN_USER or not LINKEDIN_PASSWORD:
        raise HTTPException(status_code=500, detail="Environment variables not configured")

    driver = get_driver()
    try:
        actions.login(driver, LINKEDIN_USER, LINKEDIN_PASSWORD)
        person = Person(profile_url, driver=driver)
        return person.to_dict()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        driver.quit()
