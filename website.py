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
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt
# import seaborn as sns
# import pygal
from selectors import selector

logging.basicConfig(filename='log.log', level=logging.DEBUG)
# sns.set()

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
    
    def Links_Overview(self):
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
        
    def extractAllNews(self):
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
            file = open('News.json', mode='w')
            json.dump(newsDict, file)
            file.close()
        
    def topNews(self, text=False):
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
                        print('Top News are Up to dated!')
                    else:
                        self.saving.saveText(topNews,changeInData=True)
            except FileNotFoundError:
                print('file not found, saving initial text file')
                self.saving.saveText(topNews)
        else:
            self.saving.saveCsv(topNews)
            
    def moreIndicators(self):
        pass
        
    def mainIndicators(self):
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
                
                for val in values:
                    lst = val.split()
                    while len(lst) > 5:
                        lst[0] += ' ' + lst[1]
                        lst.pop(1)

                    foundElements[lst[0]].update(
                    {
                        ribbon[1].text:lst[1],
                        ribbon[2].text:lst[2],
                        ribbon[3].text:lst[3],
                        ribbon[4].text:lst[4],
                    }
                    )  
                title = self.selenium.find_element(
                    By.XPATH, selector.TITLE
                    ).text.replace(' | World', '')
                self.saving.saveCsv(foundElements, title, transpose=True)
        except IndexError:
            pass
            to_click = self.selenium.find_elements(By.XPATH, selector.LI_RIBBON)
            to_click[0].click()
            ribbon = self.selenium.find_elements(By.XPATH, selector.TR_VALUE)
            for rib in ribbon:
                print(rib.text)
    
    def markets(self):
        linksToScrape = []
        self.selenium.find_page(self.ribbon[1])

        links = self.selenium.find_elements(By.XPATH, selector.MARKETS)
        for link in links:
            fullLink = self.ribbon[1] + link.get_attribute('href')
            linksToScrape.append(fullLink)
        
    def execute(self):
        self.Links_Overview()
        self.topNews(text=True)
        self.extractAllNews()
        self.mainIndicators()
        self.markets()
        
class Selenium(webdriver.Chrome):
    """Initiating chrome driver"""
    def __init__(self, 
                 driver= selector.DRIVER
                 ) -> None:
        super(Selenium, self).__init__()
        self.driver = driver
        self.implicitly_wait(20)
        self.maximize_window()
        self.action = ActionChains(driver)
        
    def find_page(self, givenUrl):
        self.get(givenUrl)
        print(self.get_network_conditions)
        
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
            
    def actionChain(self):
        pass
        
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
            
    def saveCsv(self, data, fileName:str, transpose:bool=False):
        with self.changeDir(self.path1):
            if transpose: 
                dataFrame = pd.DataFrame(data).T
                dataFrame.to_csv(f'{fileName}.csv')
            else:
                dataFrame = pd.DataFrame(data)
                dataFrame.to_csv(f'{fileName}.csv')
            
    def saveText(self, data, changeInData:bool=False):
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
# inst1 = Website()
# inst1.execute()

class Analyze(SaveConvention):
    
    """This class stores values taken from scraped 
    files and does various analysis on them"""
    def __init__(self,csvFile:list, jsonFile:list, textFile:list) -> None:
        super().__init__()
        self.csvFile = csvFile
        self.json = jsonFile
        self.text = textFile
        
    def nlp_nlu_news(self, givenFile=''):
        if givenFile and givenFile.endswith('.txt'):
            pass
        else:
            # json 
            print('file extension is incorrect')
    def nlp_nlu_rankings(self):
        pass
    
    def scatter_Plot(self):
        pass
    
    def bar_Plot(self, barh=False):
        if barh:
            pass
        pass
    
    def heatmap(self):
        pass
    
    def elbow_method(self, data, knum=10):
        pass
        
    def cluster(self, cluster):
        combined = self.combine_files('', '')
        pass
           
    def Highest_lowest_ranks(self, rateFile):
        pass
    
    def combine_files(self, first, second):
        with self.changeDir(path=self.path1):
            pass
    
    def save_result(self, *args, typeSave):
        typesAllowed = ['.jpg', '.png', '.jpeg']
        with self.changeDir(self.path2):
            for element in args:
                if typeSave in typesAllowed:
                    plt.savefig(f'{element}.{typeSave}')
                    print(f'{element}.{typeSave} stored in {self.path2}')
                else:
                    return
                
    def rates_on_map(self, rate):
        pass
    
a = Analyze(['Inflation Rate.csv'])
a.scatter()
