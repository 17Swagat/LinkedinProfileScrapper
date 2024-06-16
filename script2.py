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

    # Wait: For redirection:
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
    # Fetch: [Profile-URL-Links]
    profile_urls = []
    for profile in soup.select('a[href*="/in/"]'):
        url = profile['href']
        if url.startswith('/in/') or '/in/' in url:
            # full_url = f"https://www.linkedin.com{url}"
            full_url = f"{url}"
            if full_url not in profile_urls:
                profile_urls.append(full_url)
        if len(profile_urls) >= 10: #5:
            break

    return profile_urls



def scrape_profile_data(driver, profile_url, index):
    # Open a new tab
    driver.execute_script("window.open('');")
    driver.switch_to.window(driver.window_handles[-1])
    driver.get(profile_url)

    # Waiting for the profile page to load:
    time.sleep(5)
    
    # Parse the profile page with BeautifulSoup
    soup = BeautifulSoup(driver.page_source, 'html.parser')

    # Extract profile data:
    profile_data = {}
    # ✅✅✅
    profile_data['name'] = soup.find('h1', class_='text-heading-xlarge').get_text(strip=True) if soup.find('h1', class_='text-heading-xlarge') else None
    profile_data['headline'] = soup.find('div', class_='text-body-medium').get_text(strip=True) if soup.find('div', class_='text-body-medium') else None
    profile_data['identify_as'] = soup.find('span', class_='text-body-small').get_text(strip=True) if soup.find('span', class_='text-body-small') else None
    ###########################################################################################
    
    # Moving Through sections (about, education, experience)
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
            profile_data.update({
                'about': about_text
            })

        elif section_name == 'education':
            # educational-institutes:
            all_edus = section.find('ul').find_all('li', recursive=False)
            
            # Ensure 'education' key exists and is a list
            if 'education' not in profile_data:
                profile_data['education'] = []
            
            for institute in all_edus:
                info_count = len(institute)
                
                # Create a dictionary for the current institute's information
                institute_data = {}
                
                # info_count:
                # 4 + 1 = 5   : Institute_Name, Degree
                # 7 + 1 = 8   : Institute_Name, Degree, Duration

                if info_count == 5:
                    institute_data = {
                        'Institute_Name': institute.find_all('span')[1].get_text(strip=True),
                        'Degree': institute.find_all('span')[3].get_text(strip=True)
                    }
                
                elif info_count == 8:
                    institute_data = {
                        'Institute_Name': institute.find_all('span')[1].get_text(strip=True),
                        'Degree': institute.find_all('span')[4].get_text(strip=True),
                        'Duration': institute.find_all('span')[7].get_text(strip=True),
                    }

                else:
                    print(info_count)
                    print('CASE NOT EXPECTED\n')
                
                # Append the current institute's information to the 'education' list
                profile_data['education'].append(institute_data)



            
            '''

            len(section.find('ul').find_all('li', recursive=False))

            section.find('ul').find_all('li', recursive=False)
            --------------------------------------------------------------------

            len(section.find('ul').find_all('li', recursive=False)) = 2
            
            len(section.find('ul').find_all('li', recursive=False)[0].find_all('span')) = 8
            len(section.find('ul').find_all('li', recursive=False)[1].find_all('span')) = 8

            # Institute:
            section.find('ul').find_all('li', recursive=False)[0].find_all('span')[0].get_text(strip=True)
            section.find('ul').find_all('li', recursive=False)[0].find_all('span')[1].get_text(strip=True)
            # degree:
            section.find('ul').find_all('li', recursive=False)[0].find_all('span')[4].get_text(strip=True)
            # duration:
            section.find('ul').find_all('li', recursive=False)[0].find_all('span')[7].get_text(strip=True)

            --------------------------------------------------------------------

            '''

            ...
        elif section_name == 'experience':
            # all-experiences
            all_exps = section.find('ul').find_all('li', recursive=False)
            
            # Ensure 'experience' key exists and is a list
            if 'experience' not in profile_data:
                profile_data['experience'] = []
            
            # Going through all experiences
            for exp in all_exps:
                info_count = len(exp)
                
                # Create a dictionary for the current job's information
                job_data = {}
                
                # info_count:
                # 4 + 1 = 5   : Role, CompanyName
                # 7 + 1 = 8   : Role, CompanyName, Duration(Time)
                # 10 + 1 = 11 : Role, CompanyName, Duration(Time), Location
                # 12 + 1 = 13 : Role, CompanyName, Duration(Time), Location, Description

                if info_count == 5:
                    job_data = {
                        'role': exp.find_all('span')[1].get_text(strip=True),
                        'company': exp.find_all('span')[4].get_text(strip=True)
                    }
                
                elif info_count == 8:
                    job_data = {
                        'role': exp.find_all('span')[1].get_text(strip=True),
                        'company': exp.find_all('span')[4].get_text(strip=True),
                        'duration': exp.find_all('span')[7].get_text(strip=True),
                    }

                elif info_count == 11:
                    job_data = {
                        'role': exp.find_all('span')[1].get_text(strip=True),
                        'company': exp.find_all('span')[4].get_text(strip=True),
                        'duration': exp.find_all('span')[7].get_text(strip=True),
                        'location': exp.find_all('span')[10].get_text(strip=True)
                    }

                elif info_count == 13:
                    job_data = {
                        'role': exp.find_all('span')[1].get_text(strip=True),
                        'company': exp.find_all('span')[4].get_text(strip=True),
                        'duration': exp.find_all('span')[7].get_text(strip=True),
                        'location': exp.find_all('span')[10].get_text(strip=True),
                        'job-description': exp.find_all('span')[12].get_text(strip=True)
                    }

                else:
                    print(info_count)
                    print('CASE NOT EXPECTED\n')
                
                # Append the current job's information to the 'experience' list
                profile_data['experience'].append(job_data)

        
            
            '''
            # [ROUGH-WORK {some-tests}]:
            # len(section.find('ul').find_all('li', recursive=False)) = 2
            # 
            all_exps = section.find('ul').find_all('li', recursive=False)
            for exp in all_exps:
                ...

            # ver 1 ✅ title
            section.find('ul').find_all('li', recursive=False)[0].find('span', {'class': 'visually-hidden'}).get_text(strip=True)  
            # ver 2
            section.find('ul').find_all('li', recursive=False)[0].find_all('span')  
            

            # xxx 1
            len(section.find('ul').find_all('li', recursive=False))
            
            len(section.find('ul').find_all('li', recursive=False)[1].find_all('span'))
            
            section.find('ul').find_all('li', recursive=False)[1].find_all('span')[0].get_text(strip=True)
            # 
            '''
            
        
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
