import getpass
import time
import json
import os
from . import constants as const
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

def __prompt_email_password():
  u = input("Email: ")
  p = getpass.getpass(prompt="Password: ")
  return (u, p)

def _get_cookie_for_user(email):
    cookies_path = os.path.join(os.path.dirname(__file__), '..', 'cookies.json')
    if os.path.exists(cookies_path):
        with open(cookies_path, 'r') as f:
            cookies = json.load(f)
        return cookies.get(email)
    return None

def _save_cookie_for_user(email, cookie):
    cookies_path = os.path.join(os.path.dirname(__file__), '..', 'cookies.json')
    cookies = {}
    if os.path.exists(cookies_path):
        with open(cookies_path, 'r') as f:
            cookies = json.load(f)
    cookies[email] = cookie
    with open(cookies_path, 'w') as f:
        json.dump(cookies, f)

def _delete_cookie_for_user(email):
    cookies_path = os.path.join(os.path.dirname(__file__), '..', 'cookies.json')
    if os.path.exists(cookies_path):
        with open(cookies_path, 'r') as f:
            cookies = json.load(f)
        if email in cookies:
            del cookies[email]
            with open(cookies_path, 'w') as f:
                json.dump(cookies, f)

def page_has_loaded(driver):
    page_state = driver.execute_script('return document.readyState;')
    return page_state == 'complete'

def login(driver, email=None, password=None, timeout=10, redirect_url=None, force_refresh=False):
    if not force_refresh:
        cookie = None
        if email:
            cookie = _get_cookie_for_user(email)
        if cookie:
            if _login_with_cookie(driver, cookie, redirect_url=redirect_url):
                return True
            else:
                _delete_cookie_for_user(email)
        
    # Si no hay cookie válida, pedir credenciales
    if not email or not password:
        email, password = __prompt_email_password()
    driver.get("https://www.linkedin.com/login")
    element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "username")))
    email_elem = driver.find_element(By.ID,"username")
    email_elem.send_keys(email)
    password_elem = driver.find_element(By.ID,"password")
    password_elem.send_keys(password)
    password_elem.submit()
    if driver.current_url == 'https://www.linkedin.com/checkpoint/lg/login-submit':
        remember = driver.find_element(By.ID, const.REMEMBER_PROMPT)
        if remember:
            remember.submit()
    
    # Esperar el elemento solo para asegurar que la página cargó
    element = WebDriverWait(driver, timeout).until(EC.presence_of_element_located((By.CLASS_NAME, const.VERIFY_LOGIN_ID)))
    # Obtener la cookie li_at y guardarla
    for c in driver.get_cookies():
        if c['name'] == 'li_at':
            _save_cookie_for_user(email, c['value'])
            break
    # Redirigir si se especifica una URL
    if redirect_url:
        driver.get(redirect_url)
    return True
  
def _login_with_cookie(driver, cookie, redirect_url=None):
    driver.get("https://www.linkedin.com")
    driver.delete_all_cookies()
    driver.add_cookie({
        "name": "li_at",
        "value": cookie,
        "domain": ".linkedin.com"
    })
    
    if redirect_url:
        driver.get(redirect_url)
    else:
        driver.get("https://www.linkedin.com/feed")
    # Si el login fue exitoso, retorna True
    # Considerar exitoso si la cookie está presente y la página carga
    if driver.get_cookie("li_at"):
        return True
    return False
