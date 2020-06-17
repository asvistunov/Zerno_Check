#!/usr/bin/env python
# coding: utf-8

# In[2]:

## test

import requests
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
from dateutil.parser import parse
import time
from datetime import datetime 

# In[3]:
token = "1171007024:AAGxwY_kQ0w2lpG1KrVutwY6P5n_fDQQoVs"
html = 'https://belgorod.zol.ru'

class BotHandler:
    
    def __init__(self, token):
        self.token = token
        self.api_url = f'https://api.telegram.org/bot{token}/'
        self.html = html
        
    def get_updates(self, offset=None, timeout=30):
        method = 'getUpdates'
        params = {'timeout': timeout, 'offset' : offset}
        resp = requests.get(self.api_url + method, params)
        result_json = resp.json()['result']
        return result_json
    
    def send_message(self, chat_id, text):
        params = {'chat_id': chat_id, 'text': text}
        method = 'sendMessage'
        resp = requests.post(self.api_url + method, params)
        return resp
    
    def send_file(self, chat_id, document):
        params = {'chat_id': chat_id, 'document': document}
        method = 'sendDocument'
        resp = requests.post(self.api_url + method, params)
        return resp
        
    def get_last_update(self):
        get_result = self.get_updates()

        if len(get_result) > 0:
            last_update = get_result[-1]
        else:
            last_update = None
        return last_update
    
    def last_text(self):
        last_text = self.get_last_update()['message']['text']
        return last_text
    
    def is_date(self, string, fuzzy=False):
        try: 
            parse(string, fuzzy=fuzzy)
            return True
        except ValueError:
            return False

    def final_table(self):
        html_for_parse = requests.get(self.html).content
        soup = BeautifulSoup(html_for_parse)
        raw_html = str(soup.select('#table_offers')[0])
        df = pd.read_html(raw_html)
        zerno_table = df[0]
        zerno_table.columns = zerno_table.iloc[0]
        zerno_table = zerno_table[pd.isna(zerno_table['Время']) == False].iloc[2:,:]
        zerno_table = zerno_table.replace(np.nan, '', regex=True)
        zerno_table = zerno_table[zerno_table['Регион'].apply(self.is_date) == False]
        return zerno_table
    
    def details(self):
        html_for_parse_2 = requests.get(self.html).content
        soup_2 = BeautifulSoup(html_for_parse_2)
        raw_html_2 = soup_2.select('#table_offers')[0]
        raw_html_2 = raw_html_2.find_all('table')
        link = raw_html_2[0].find('a').get('href')
        html_for_further_parse = requests.get(link).content
        needed_table = BeautifulSoup(html_for_further_parse)
        needed_table = needed_table.find_all('table')
        needed_table = str(needed_table)
        table_with_info = pd.read_html(needed_table)[0].iloc[:,:2]
        reques = []
        for dic in dict(table_with_info.set_index(0).loc[['Автор','Телефон']])[1]:
            if 'Сообщение' and 'автору' in dic.split(' '):
                dic = ' '.join(dic.split(' ')[:2])
            reques.append(dic)
        reques = f'{reques[0]} {reques[1]}'
        return reques
    
ZernoCheckerBot = BotHandler(token)

# In[ ]:

ZernoCheckerBot = BotHandler(token)
def main():
    new_offset = None
    site_last_upd = ZernoCheckerBot.final_table().iloc[0,:]
    all_chat_ids = []
    while True:
        ZernoCheckerBot.get_updates(new_offset)
        last_update = ZernoCheckerBot.get_last_update()
        if last_update == None: continue
        last_update_id = last_update['update_id']
        last_chat_id = last_update['message']['chat']['id']
        last_chat_name = last_update['message']['chat']['first_name']
        last_chat_text = last_update['message']['text']
        
        if last_chat_id not in all_chat_ids:
            all_chat_ids.append(last_chat_id)
        if ZernoCheckerBot.final_table().iloc[0,:].equals(site_last_upd) == False:
            for i in all_chat_ids:
                ZernoCheckerBot.send_message(i , str(list(ZernoCheckerBot.final_table().iloc[0,:])))
                ZernoCheckerBot.send_message(i , ZernoCheckerBot.details())
                site_last_upd = ZernoCheckerBot.final_table().iloc[0,:]
        if last_chat_text.lower() == 'ты работаешь?':
            ZernoCheckerBot.send_message(last_chat_id, 'Да')
        if last_chat_text.lower() == 'время':
            ZernoCheckerBot.send_message(last_chat_id, datetime.now().strftime('%H:%M:%S') ) 

if __name__ == '__main__':  
    try:
        main()
    except KeyboardInterrupt:
        exit() 

