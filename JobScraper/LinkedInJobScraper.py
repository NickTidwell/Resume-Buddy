import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
from urllib.parse import urlparse, parse_qs

class LinkedInJobScraper:https://webcourses.ucf.edu/profile/settings
    def __init__(self, url):
        self.url = url
        self.driver = self._set_up_driver()
        self.extracted_jobs = []

    def _set_up_driver(self):
        options = webdriver.ChromeOptions()
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
        driver = webdriver.Chrome(options=options)
        return driver
    
    def scrape_jobs(self):
        # Open the LinkedIn job search page
        self.driver.get(self.url)
        self.driver.implicitly_wait(10)

        # Find the job listings
        job_count = len(self.driver.find_elements(By.XPATH, '//*[@id="main"]/div/div[2]/div[1]/div/ul/li'))

        # Extract job details one by one
        for i in range(1, job_count + 1):
            job_xpath = f'//*[@id="main"]/div/div[2]/div[1]/div/ul/li[{i}]'
            job = self.driver.find_element(By.XPATH, job_xpath)
            job.click()
            time.sleep(0.1)
            anchor_elements = job.find_element(By.TAG_NAME, 'a')
            href = anchor_elements.get_attribute('href')
            job_title = anchor_elements.get_attribute('aria-label')
            company = job.find_element(By.CLASS_NAME, 'job-card-container__primary-description').text
            job_description = self.driver.find_element(By.XPATH, '//*[@id="job-details"]/div').text
            job_id = job.get_attribute("data-occludable-job-id")
            self.extracted_jobs.append({
                "href": href,
                "job_title": job_title,
                "company": company,
                "description": job_description,
                'job_id': job_id
            })


    def save_jobs_to_json(self, output_path):
        with open(output_path, 'w') as json_file:
            json.dump(self.extracted_jobs, json_file, indent=4)

    def close_driver(self):
        self.driver.quit()

# Usage example:
jobs_names = ["Financial Analyst", "Teacher", "Software Engineer", "Graphic Designer", "Registered Nurse", "Physical Therapist"]
for job in jobs_names:
    encoded_job = job.replace(' ', '%20')
    scraper = LinkedInJobScraper(f"https://www.linkedin.com/jobs/search/?keywords={encoded_job}")
    scraper.scrape_jobs()
    scraper.save_jobs_to_json(f'{job}.json')
    scraper.close_driver()
