import os
import json
from dotenv import load_dotenv
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from config.config import BASE_URL, LOGGED_IN_URL, LOGIN_API_URL, SENSOR_INFO_URL, START_URL

load_dotenv(override=True)
USERNAME = os.getenv("PORTAL_USERNAME")
PASSWORD = os.getenv("PORTAL_PASSWORD")

if not USERNAME or not PASSWORD:
    raise RuntimeError("Missing USERNAME or PASSWORD, Please Check .env file")

# -------------------------------------------------
# BACKEND CREDENTIAL CHECK
# -------------------------------------------------
def validate_credentials() -> None:
    response = requests.post(
        LOGIN_API_URL,
        data={
            "login": USERNAME,
            "password": PASSWORD,
        },
        headers={
            "Content-Type": "application/x-www-form-urlencoded",
        },
        timeout=10,
    )

    if response.status_code < 200 or response.status_code >= 300:
        raise RuntimeError("Credential validation failed")

    print("Backend credential check passed")

# -------------------------------------------------
# BROWSER LOGIN
# -------------------------------------------------
def browser_login():
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    # Docker-only flags
    if os.getenv("RUNNING_IN_DOCKER") == "1":
        options.binary_location = "/usr/bin/chromium"
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")

    # IMPORTANT: do NOT pass Service()
    driver = webdriver.Chrome(options=options)
    try:
        driver.get(START_URL)
        wait = WebDriverWait(driver, 20)

        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "#login")))

        driver.execute_script(
            'document.querySelector("#login").value = arguments[0];',
            USERNAME,
        )
        driver.execute_script(
            'document.querySelector("#password").value = arguments[0];',
            PASSWORD,
        )

        driver.execute_script(
            'document.querySelector("button#loginButton").click();'
        )

        wait.until(lambda d: LOGGED_IN_URL in d.current_url)

        print("Login successful")
        return driver.get_cookies()

    finally:
        driver.quit()

# -------------------------------------------------
# SESSION CREATION
# -------------------------------------------------
def create_authenticated_session(cookies) -> requests.Session:
    session = requests.Session()

    for cookie in cookies:
        session.cookies.set(
            name=cookie["name"],
            value=cookie["value"],
            path=cookie.get("path", "/"),
        )

    session.headers.update({
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/json",
        "Referer": START_URL,
    })

    return session

# -------------------------------------------------
# AUTHENTICATED API CALL
# -------------------------------------------------
def call_authenticated_api(session) -> dict:
    response = session.get(SENSOR_INFO_URL, timeout=10)

    if response.status_code == 401:
        raise RuntimeError("Session not authenticated")

    response.raise_for_status()
    data = response.json()

    #print(json.dumps(data, indent=2, ensure_ascii=False))
    return data
