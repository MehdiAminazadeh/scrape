import requests
import re
import logging
import os
import json

from bs4 import BeautifulSoup
from collections import defaultdict
from contextlib import contextmanager
from time import ctime, sleep
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from requests.exceptions import ConnectionError
from pathlib import Path
import pandas as pd
from selectors import selector

logging.basicConfig(filename='log.log', level=logging.DEBUG)

class Website:
    def __init__(self) -> None:
        self.mainUrl = 'https://tradingeconomics.com/'
        self.selenium = Selenium()
        self.saving = SaveConvention()
        
    def makeSoup(self, givenUrl):
        try:
            req = requests.get(givenUrl, headers={'User-Agent':selector.USER_AGENT})
            return BeautifulSoup(req.content, features='html.parser')
        
        except ConnectionError as ce: 
            return f'{ce} enable vpn'
    
    def links_overview(self):
        dict1 = defaultdict(dict)
        dict2 = {}
        ribbonLst = []
        countries = ['united-states', 'united-kingdom', 'china',
                     'brazil', 'italy', 'germany',
                     'euro-area',]
        
        ribbon = ['calendar', 'stream',
                  'indicators', 'countries',]
        page = self.makeSoup(self.mainUrl)
        
        try:
            for anchor in page.findAll('a', href=True):
                for country in countries:
                    if anchor['href'].startswith(f'/{country}'):
                        if len(anchor.text) < 50:
                            dict2[anchor['href']] = anchor.text.strip()
                            for key, value in dict2.items():
                                if key.startswith(f'/{country}/'):
                                    dict1[country].update({key.replace(f'/{country}/', ''):value})
            for rib in ribbon:
                ribbonLst.append(self.mainUrl + rib)
                
        except AttributeError:
            print('Problem with the internet')
        
        finally:   
            self.countryDict = dict1
            self.ribbon = ribbonLst
            self.saving.save_csv(self.countryDict, 'Overview')
            
    def extract_allnews(self):
        newsDict = defaultdict(dict)
        self.selenium.find_page(self.ribbon[1])
        self.selenium.scroll(5)
        news = self.selenium.find_elements(By.XPATH,selector.NEWS)
        header = self.selenium.find_elements(By.XPATH, selector.HEADER)
        
        for new, head in zip(news, header):
            if len(new.text) > len(head.text):
                newsDict[head.text].update({
                    'News': new.text.replace('\n', ',')
                })
        if 'News.json' in os.listdir(self.saving.path1):
            print('Already available')
            
        else:
            with self.saving.changeDir(self.saving.path1):
                file = open('News.json', mode='w')
                json.dump(newsDict, file)
                file.close()
        
    def top_news(self, text=False):
        topNews = []
        page = self.makeSoup(self.mainUrl)
        news = page.find('div', class_='col-md-8')
        regex = re.compile(r'\d+\s(min(s)?|hour(s)|day(s))\sago')
        newsSub = re.sub(regex,'', news.text.strip())
        split = newsSub.split('\n')
        
        for string in split:
            if len(string) < 100:
                continue
            else:
                topNews.append(string)
        topNews.insert(0, ctime())
        
        if text:
            try:
                with open('data.txt', 'r') as text:
                    lineOne = text.readlines()
                    if lineOne[1] == topNews[1]:
                        print('Top News are Updated!')
                    else:
                        self.saving.save_text(topNews,changeInData=True)
            except FileNotFoundError:
                print('file not found, saving initial text file')
                self.saving.save_text(topNews)
        else:
            self.saving.save_csv(topNews)
        
    def main_indicators(self):
        self.selenium.find_page(self.ribbon[-2])
        indicatorHref = self.selenium.find_elements(
            By.XPATH, selector.INDICATOR_LINKS
            )
        links = [link.get_attribute('href') for link in indicatorHref] 
        foundElements = defaultdict(dict)
        
        try:
            for link in links:

                self.selenium.find_page(link)
                world = self.selenium.find_elements(
                    By.XPATH, selector.LI_RIBBON
                    )[0]
                world.click()
                ribbon = self.selenium.find_elements(By.XPATH, selector.TH_RIBBON)
                values = [value.text for value
                        in self.selenium.find_elements(
                            By.XPATH, selector.TR_VALUE
                        )]
                if len(ribbon) > 5:
                    continue

                for value in values:
                    lst = value.split()
                    if len(lst) < 2:
                        continue

                    else:
                        while len(lst) > 5:
                            lst[0] += ' ' + lst[1]
                            lst.pop(1)
                            
                    title = self.selenium.find_element(
                    By.XPATH, selector.TITLE
                    ).text.replace(' | World', '')
                    
                    foundElements[lst[0]].update(
                    {
                        title:lst[1],
                        # ribbon[4].text + f'_{title}': lst[4]
                    }
                    )
                self.saving.save_csv(foundElements, 'indicators', transpose=True)
        except IndexError:
            pass


    def markets(self):
        self.selenium.find_page(self.mainUrl)
        links = [link.get_attribute('href')
                 for link in self.selenium.find_elements(By.XPATH, selector.MARKET)] 
        
        part_one = links[:5]
        part_two = links[5:]
        dict_ = {}
        for link in part_one:
            self.selenium.find_page(link)
        tbody, thead = (self.selenium.find_elements(By.XPATH, '//tbody'),
                            self.selenium.find_elements(By.XPATH, '//thead'))
    
        for head, body in zip(thead, tbody):
            head_split = re.split('\n', head.text)
            body_split = re.split('\n', body.text)

            # print(body_split)
        

    def execute(self):
        self.links_overview()
        self.top_news(text=True)
        self.extract_allnews()
        self.main_indicators()
        self.markets()
        
class Selenium(webdriver.Chrome):
    """Initiating chrome driver"""
    
    def __init__(self, driver= selector.DRIVER,) -> None:
        super(Selenium, self).__init__()

        self.driver = driver
        self.implicitly_wait(20)
        self.maximize_window()
        self.action = ActionChains(driver)


    def find_page(self, givenUrl:str) -> None:
        self.get(givenUrl)
        self.get_network_conditions
        
        
    def scroll(self, limit:int, pause:int=2) -> None:
        scroll_count = 0
        prev_height = self.execute_script(selector.PAGE_HEIGHT)
        
        while True and scroll_count < limit:
            self.execute_script(selector.SCROLL)
            sleep(pause)
            new_height = self.execute_script(selector.PAGE_HEIGHT)
            if new_height == prev_height:
                break
            prev_height = new_height
            scroll_count += 1
        
class SaveConvention(object):
    def __init__(self) -> None:
        #hard coded paths 
        self.path1 = os.path.join(os.path.dirname(__file__), 'result')
        self.path2 = os.path.join(os.path.dirname(__file__), 'pltFigs') 
    
    def __repr__(self) -> str:
        print('Paths available: {0}\n{1}'.format(self.path1, self.path2))
    
    @contextmanager
    def changeDir(self, path):
        origin = Path().absolute()
        try:
            os.chdir(path)
            yield
        finally:
            os.chdir(origin)
   
    def save_csv(self, data, fileName:str, transpose:bool=False):
        with self.changeDir(self.path1):
            if transpose: 
                dataFrame = pd.DataFrame(data).T
                dataFrame.to_csv(f'{fileName}.csv')
            else:
                dataFrame = pd.DataFrame(data)
                dataFrame.to_csv(f'{fileName}.csv')

    def save_text(self, data, changeInData:bool=False)-> None:
        with self.changeDir(self.path1):
            if changeInData:
                with open('data.txt', 'r') as textRead:
                    with open('data.txt', 'w') as textWrite:
                        prevData = textRead.read()
                        newData = prevData + '\n'.join(data)
                        textWrite.write(newData)
            else: 
                with open('data.txt', 'w') as text:
                    string = '\n'.join(data)
                    text.write(string)

if __name__ == '__main__':
    instance = Website()
    instance.execute()
