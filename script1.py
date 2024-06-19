"""
API:
______________________________________________________________________
* Unable to find a Free API [with unlimited no. of free api calls]
* Or a python package/library to freely scrape Linkedin Profile Info.

* [Here, I've used the `Scrapingdog` API, which provides 5 requests to get
   profile information. Have already used 1 already.]

* The given script output's User Profile infos into .json files in the Current Working Directory.
* Code for converting the json data into a .csv was NOT DONE.

* Demo: Was not able to record a working demo of this script as the free trials finised.
        But the script works when a valid API key is given.
_______________________________________________________________________
"""

# scrapingdog:
import requests
import json
import time
from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import time
import json
from bs4 import BeautifulSoup

# pswd-hiding:
import stdiomask
import os

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

URL_scrapingdog = "https://api.scrapingdog.com/linkedin/"
API_KEY = ""
INDEX = 0


def login(driver, username, password):
    driver.get("https://www.linkedin.com/login")
    time.sleep(2)

    email_field = driver.find_element(By.ID, "username")
    email_field.send_keys(username)

    password_field = driver.find_element(By.ID, "password")
    password_field.send_keys(password)
    password_field.send_keys(Keys.RETURN)
    time.sleep(2)

    # verfication-page:
    wait_for_verification(driver=driver)


def wait_for_verification(driver):
    verification_link_contains = "https://www.linkedin.com/checkpoint/challenge/"

    # Wait: For redirection:
    time.sleep(5)
    current_page_link = driver.current_url

    try:
        if verification_link_contains in current_page_link:
            print(
                "Verification page detected. Waiting for user to complete the verification..."
            )
            WebDriverWait(driver, timeout=600).until(
                lambda d: verification_link_contains not in d.current_url
            )
            print("User has completed the verification.")
    except TimeoutException:
        print("Verification not completed in time. Exiting.")
        driver.quit()
        exit(1)


def search_users_nd_getdata(driver, first_name, last_name):
    """
    SEARCHES FOR THE GIVEN (FName & LName) and then returns the Profile URLS of the
    First 5 profiles:
    """

    time.sleep(3)

    # Click on [search] button:
    search_button = driver.find_element(
        By.XPATH, "//button[@aria-label='Click to start a search']"
    )
    search_button.send_keys(Keys.RETURN)
    time.sleep(2)

    # Enter name in [Search] box & [Enter]:
    search_box = driver.find_element(By.CLASS_NAME, "search-global-typeahead__input")
    search_box.send_keys(f"{first_name} {last_name}")
    search_box.send_keys(Keys.RETURN)
    time.sleep(3)

    # Click on the [people] button:
    people_button = driver.find_element(
        By.XPATH,
        "//button[contains(@class, 'artdeco-pill') and contains(@class, 'search-reusables__filter-pill-button') and @type='button' and text()='People']",
    )
    people_button.click()
    time.sleep(3)

    soup = BeautifulSoup(driver.page_source, "html.parser")

    # Fetch: First 5 [Profile-URL-Links]:
    profile_urls = []
    for profile in soup.select('a[href*="/in/"]'):
        url = profile["href"]
        if url.startswith("/in/") or "/in/" in url:
            full_url = f"{url}"
            if full_url not in profile_urls:
                profile_urls.append(full_url)
        if len(profile_urls) >= 5:
            break

    driver.quit()

    # Fetching Profile Data:
    for url in profile_urls:
        get_profile_info(url)


def get_profile_info(profile_url):
    """
    Outputs: A .json file with profile info
    """
    global INDEX
    params = {"api_key": API_KEY, "type": "profile", "linkId": profile_url}
    try:
        response = requests.get(URL_scrapingdog, params=params)
        if response.status_code == 200:
            data = response.json()
            file_name = f"script_1_profile_{INDEX+1}_info.json"
            INDEX += 1
            with open(os.path.join("script1_data", file_name), "w") as json_file:
                json.dump(data, json_file, indent=4)
                print(f'Data dumped into: {file_name}')
        else:
            print("Request Failed!!")
            print("Status_code:", response.status_code)

    except Exception as e:
        print("Request Failed!!")
        print("Your API Requests Credits might have finished!!")
        print(e)


def main(first_name, last_name, email, password):
    driver = webdriver.Edge()
    try:
        login(driver, email, password)
        search_users_nd_getdata(driver, first_name, last_name)
    except Exception as e:
        print("Some Error Occured!!")
        print(f"{e}")


if __name__ == "__main__":

    email = input("Enter your Username/Email(Linkedin): ")
    password = stdiomask.getpass("Enter your Password: ", "*")
    fname = input("Enter First Name: ")
    lname = input("Enter Last Name: ")
    api_key = stdiomask.getpass("Enter your [ScrapingDog API]: ", "*")

    API_KEY = api_key

    main(fname, lname, email, password)
