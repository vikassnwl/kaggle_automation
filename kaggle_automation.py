from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import time
from tqdm import tqdm
import os, re


class KaggleAutomation:
    def __init__(self):
        ...

    def get_urls(self, html_file_path):
        html_content = open(html_file_path).read()
        soup = BeautifulSoup(html_content, 'lxml')
        links = soup.find_all('a')
        hrefs = []
        for link in links:
            href = link.get('href')
            if href and "scriptVersionId" in href:
                hrefs.append(href)
        return hrefs

    def fetch_scores(self, html_file_path, sleep=2):
        service = Service(executable_path=f"{os.path.dirname(__file__)}/chromedriver")
        driver = webdriver.Chrome(service=service)
        urls = self.get_urls(html_file_path)
        self.versions = []
        self.pub_scores = []
        for url in tqdm(urls):
            driver.get(url)
            time.sleep(sleep)
            html_content = driver.page_source
            soup = BeautifulSoup(html_content, 'lxml')
            try:
                # p_content = soup.findAll('p', class_='sc-dENhDJ sc-lopgLL fTZFV hqBFNM')[1].text
                p_content = soup.select("p.sc-dENhDJ.fTZFV")[-1].text.strip()
                # assert(p_content[-1]!="s")  # invalid: 298.1s  valid: 74430.75684
                pattern = r"^\d+(\.\d+)?$"
                assert(re.match(pattern, p_content))  # {"invalid": ["298.1s", "35853.8s - GPU T4 x2"], "valid": ["74430.75684", "74430"]}
                span_content = soup.findAll('span', class_='sc-gLXSEc kLwwHW')[-1].text.strip()
            except Exception as e:
                continue
            self.versions.append(span_content)
            self.pub_scores.append(p_content)

        driver.quit()

    def print_scores(self):
        print(f"{'Notebook Version':20}{'Public Score'}")
        print(f"{len('Notebook Version')*'-':20}{len('Public Score')*'-'}")
        for version, pub_score in zip(self.versions, self.pub_scores):
            print(f"{version:20}{pub_score}")