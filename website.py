import requests
import re
import logging
import os
import json

from bs4 import BeautifulSoup
import pandas as pd
from collections import defaultdict
from contextlib import contextmanager
from time import ctime, sleep
from selenium import webdriver
from selenium.webdriver.common.by import By
from requests.exceptions import ConnectionError

from selectors import selector

logging.basicConfig(filename='log.log', level=logging.DEBUG)

class Website:
    def __init__(self) -> None:
        self.mainUrl = 'https://tradingeconomics.com/'
        
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
        selen = Selenium()
        save = SaveConvention()
        newsDict = defaultdict(dict)
        selen.find_page(self.ribbon[1])
        selen.scroll(5)
        news = selen.find_elements(By.XPATH,selector.NEWS)
        header = selen.find_elements(By.XPATH, selector.HEADER)
        for new, head in zip(news, header):
            if len(new.text) > len(head.text):
                newsDict[head.text].update({
                    'News': new.text.replace('\n', ',')
                })
        if 'News.json' in os.listdir(save.path):
            print('Already available')
        else:
            file = open('News.json', mode='w')
            json.dump(newsDict, file)
            file.close()
        
    def topNews(self, 
                text=False):
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
        save = SaveConvention()
        if text:
            try:
                with open('data.txt', 'r') as text:
                    lineOne = text.readlines()
                    if lineOne[1] == topNews[1]:
                        print('Top News are Up to dated!')
                    else:
                        save.saveText(topNews,changeInData=True)
            except FileNotFoundError:
                save.saveText(topNews)
        else:
            save.saveCsv(topNews)
        
    def indicators(self):
        selen = Selenium()
        selen.find_page(self.ribbon[-2])
        indicatorHref = selen.find_elements(
            By.XPATH, selector.INDICATOR_LINKS
            )
        links = [link.get_attribute('href') for link in indicatorHref] 
        foundElements = defaultdict(dict)
        save = SaveConvention()
        try:
            for link in links:
                selen.find_page(link)
                world = selen.find_elements(
                    By.XPATH, selector.LI_RIBBON
                    )[0]
                world.click()
                ribbon = selen.find_elements(By.XPATH, selector.TH_RIBBON)
                values = [value.text for value
                        in selen.find_elements(
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
                title = selen.find_element(
                    By.XPATH, selector.TITLE
                    ).text.replace(' | World', '')
                save.saveCsv(foundElements, title, transpose=True)
        except IndexError:
            pass
            to_click = selen.find_elements(By.XPATH, selector.LI_RIBBON)
            to_click[0].click()
            ribbon = selen.find_elements(By.XPATH, selector.TR_VALUE)
            for rib in ribbon:
                print(rib.text)
              
    def markets(self):
        soup = self.makeSoup(self.ribbon[4])
        pass
        
    def execute(self):
        self.Links_Overview()
        self.topNews(text=True)
        self.extractAllNews()
        self.indicators()
        # self.markets()
        
class Selenium(webdriver.Chrome):
    def __init__(self, 
                 driver= selector.DRIVER
                 ) -> None:
        super(Selenium, self).__init__()
        self.driver = driver
        self.implicitly_wait(20)
        self.maximize_window()
        
    def find_page(self, givenUrl):
        self.get(givenUrl)
        
    def scroll(self, limit:int, pause:int=2):
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
        
class SaveConvention:
    def __init__(self):
        try:
            self.path = os.path.join(os.path.dirname(__file__), 'result')
        except FileExistsError:
            pass
        
    @contextmanager
    def changeDir(self, path):
        try:
            prev_cwd = os.getcwd()
            os.chdir(path)
        finally:
            yield os.chdir(prev_cwd)
            
    def saveCsv(self, data, fileName, transpose=False):
        with self.changeDir(self.path):
            if transpose: 
                dataFrame = pd.DataFrame(data).T
                dataFrame.to_csv(f'{fileName}.csv')
            else:
                dataFrame = pd.DataFrame(data)
                dataFrame.to_csv(f'{fileName}.csv')
            
    def saveText(self, data, changeInData=False):
        with self.changeDir(self.path):
            with open('data.txt', 'w') as text:
                string = '\n'.join(data)
                text.write(string)
            if changeInData:
                with open('data.txt', 'r') as textRead:
                    with open('data.txt', 'w') as textWrite:
                        prevData = textRead.read()
                        newData = prevData + '\n'.join(data)
                        textWrite.write(newData)

inst1 = Website()
inst1.execute()

# import tensorflow as tf
# from tensorflow import keras
# from keras.preprocessing.text import Tokenizer
# from keras.utils import pad_sequences

# class AnalyzeNews:
#     def __init__(self, file) -> None:
#         self.file = open(file, 'r').readlines()[1:]
    
#     def tokenize(self):
#         tokenizer = Tokenizer(num_words=100, oov_token="<OOV>")
#         tokenizer.fit_on_texts(self.file)  
#         word_index = tokenizer.word_index
#         sequence = tokenizer.texts_to_sequences(self.file)
#         padded = pad_sequences(sequence, padding='post')
#         print(padded[0])
#         print(padded.shape)
        
# a = AnalyzeNews('data.txt')
# a.tokenize()