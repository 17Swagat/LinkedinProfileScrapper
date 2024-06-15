from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import time
import json
import csv
from bs4 import BeautifulSoup

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException


'''
sections:
        * guidance ❌
        * insights ❌
        * resources ❌
        * content_collections ❌

        * about
        * education
        * interests
        * experience
        * skills
'''

# 2.2 [PART]
SECTION_MAPPING = {
    'about': 'about',
    'education': 'education',
    'interests': 'interests',
    'experience': 'experience',
    'skills': 'skills'
}

def login_linkedin(driver, username, password):
    driver.get('https://www.linkedin.com/login')
    time.sleep(2)
    
    email_field = driver.find_element(By.ID, 'username')
    email_field.send_keys(username)
    password_field = driver.find_element(By.ID, 'password')
    password_field.send_keys(password)
    
    password_field.send_keys(Keys.RETURN)
    time.sleep(2)

    # verfication-page:
    wait_for_verification(driver=driver)
    

def wait_for_verification(driver):
    verification_link_contains = 'https://www.linkedin.com/checkpoint/challenge/'

    # Give some time for the redirection to happen, if needed
    time.sleep(5)
    current_page_link = driver.current_url

    try:
        if verification_link_contains in current_page_link:
            print("Verification page detected. Waiting for user to complete the verification...")
            WebDriverWait(driver, timeout=600).until(lambda d: verification_link_contains not in d.current_url)
            print("User has completed the verification.")
    except TimeoutException:
        print("Verification not completed in time. Exiting.")
        driver.quit()
        exit(1)


# 1.1
def search_user(driver, first_name, last_name):

    # @LATER: MIGHT-NEED TO ADD SOME SLEEP-TIME IN ORDER TO WAIT FOR THE HOME-PAGE TO LOAD
    time.sleep(3)

    # Click on [search] button:
    search_button = driver.find_element(By.XPATH, "//button[@aria-label='Click to start a search']")
    search_button.send_keys(Keys.RETURN)

    time.sleep(2)

    # OLD:
    # search_box = driver.find_element(By.XPATH, "//input[@class='search-global-typeahead__input']")
    
    # Enter name in [Search] box & [Enter]:
    search_box = driver.find_element(By.CLASS_NAME, 'search-global-typeahead__input')
    search_box.send_keys(f"{first_name} {last_name}")
    search_box.send_keys(Keys.RETURN)
    time.sleep(3)

    # Click on the [people] button:
    people_button = driver.find_element(By.XPATH, "//button[contains(@class, 'artdeco-pill') and contains(@class, 'search-reusables__filter-pill-button') and @type='button' and text()='People']")
    people_button.click()
    time.sleep(3)
    

    # 2
    # Parse the page with BeautifulSoup
    soup = BeautifulSoup(driver.page_source, 'html.parser')

    # 2.2
    # Fetch: First 5 [Profile-URL-Links]
    profile_urls = []
    for profile in soup.select('a[href*="/in/"]'):
        url = profile['href']
        if url.startswith('/in/') or '/in/' in url:
            # full_url = f"https://www.linkedin.com{url}"
            full_url = f"{url}"
            if full_url not in profile_urls:
                profile_urls.append(full_url)
        if len(profile_urls) >= 5: #10:
            break

    return profile_urls



def scrape_profile_data(driver, profile_url, index):
    # Open a new tab
    driver.execute_script("window.open('');")
    driver.switch_to.window(driver.window_handles[-1])
    driver.get(profile_url)

    # Wait for the profile page to load
    time.sleep(5)
    
    # Parse the profile page with BeautifulSoup
    soup = BeautifulSoup(driver.page_source, 'html.parser')

    # Extract profile data:
    profile_data = {}
    # ✅✅✅
    profile_data['name'] = soup.find('h1', class_='text-heading-xlarge').get_text(strip=True) if soup.find('h1', class_='text-heading-xlarge') else None
    profile_data['headline'] = soup.find('div', class_='text-body-medium').get_text(strip=True) if soup.find('div', class_='text-body-medium') else None
    profile_data['identify_as'] = soup.find('span', class_='text-body-small').get_text(strip=True) if soup.find('span', class_='text-body-small') else None
    # profile_data['location'] = soup.find('span', class_='text-body-small').get_text(strip=True) if soup.find('span', class_='text-body-small') else None
    # profile_data['about'] = soup.find('div', class_='pv-about__summary-text').get_text(strip=True) if soup.find('div', class_='pv-about__summary-text') else None



    # 2.1 [WORKED]
    # profile_info = []
    # sections = soup.find_all('section', class_='pv-profile-card')
    # for section in sections:
    #     section_name_about = section.find('div', {'id': 'about'})
    #     section_name_education = section.find('div', {'id': 'education'})
    #     section_name_interests = section.find('div', {'id': 'interests'})
    #     section_name_experience = section.find('div', {'id': 'experience'})
    #     section_name_skills = section.find('div', {'id': 'skills'})
        
    #     if section_name_about is not None:
    #         section_name = 'about'
    #     elif section_name_education is not None:
    #         section_name = 'education'
    #     elif section_name_skills is not None:
    #         section_name = 'skills'
    #     elif section_name_experience is not None:
    #         section_name = 'experience'
    #     elif section_name_interests is not None:
    #         section_name = 'interests'
    #     else:
    #         section_name = '_+_none_+_'
        # ...
    
    # 2.2
    ###########################################################################################
    sections = soup.find_all('section', class_='pv-profile-card')
    for section in sections:
        section_name = '__none__'
        
        # Check each section for the defined IDs
        for section_id, name in SECTION_MAPPING.items():
            if section.find('div', {'id': section_id}) is not None:
                # match-found
                section_name = name
                break  
        
        if section_name == '__none__':
            continue

        if section_name == 'about':
            # ✅
            span_tags = section.find_all('span', class_='visually-hidden')
            # len(span_tags) = 2
            # need the 2nd one: 
            about_text = span_tags[1].get_text(strip=True)
            profile_data['about'] = about_text
        
        elif section_name == 'education':
            ...
        elif section_name == 'experience':
            ...
        elif section_name == 'skills':
            ...
        elif section_name == 'interests':
            ...

    ###########################################################################################



    # Save profile data to a JSON file
    file_name = f'profile_info_{index}.json'
    with open(file_name, 'w') as json_file:
        json.dump(profile_data, json_file, indent=4)

    # Close the current tab and switch back to the initial tab
    driver.close()
    driver.switch_to.window(driver.window_handles[0])





def main(first_name, last_name, username, password):
    # driver = webdriver.Chrome()
    driver = webdriver.Edge()
    try:
        login_linkedin(driver, username, password)
        profile_urls = search_user(driver, first_name, last_name)

        # Scrape each profile URL and save data
        for index, profile_url in enumerate(profile_urls):
            scrape_profile_data(driver, profile_url, index + 1)

    finally:
        driver.quit()


if __name__ == "__main__":
    main('swagat', 'baruah', '17swagat@gmail.com', 'thereisablackhole17')