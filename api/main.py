import os
import time
import json
from dotenv import load_dotenv
from fastapi import FastAPI, Query, HTTPException, Response
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

@app.get("/refresh_linkedin_cookie")
def refresh_linkedin_cookie():
    if not CHROMEDRIVER_PATH or not LINKEDIN_USER or not LINKEDIN_PASSWORD:
        raise HTTPException(status_code=500, detail="Environment variables not configured")

    driver = get_driver()
    try:
        actions.login(driver, LINKEDIN_USER, LINKEDIN_PASSWORD, force_refresh=True)
        return {"ok": True, "msg": "Cookie refreshed"}
    finally:
        driver.quit()

@app.get("/scrape_person")
def scrape_person(profile_url: str = Query(..., description="LinkedIn profile URL")):
    if not CHROMEDRIVER_PATH or not LINKEDIN_USER or not LINKEDIN_PASSWORD:
        raise HTTPException(status_code=500, detail="Environment variables not configured")

    start_time = time.time()
    driver = get_driver()
    try:
        actions.login(driver, LINKEDIN_USER, LINKEDIN_PASSWORD)
        person = Person(profile_url, driver=driver)
        elapsed = time.time() - start_time
        result = person.to_dict()
        return Response(
            content=json.dumps({
                "status": 200,
                "data": result,
                "elapsed": elapsed
            }),
            media_type="application/json",
            status_code=200
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        driver.quit()
