#!/usr/bin/env python
# coding: utf-8

# In[81]:


import requests
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
from dateutil.parser import parse
import re
import time
from datetime import datetime


# In[104]:


token = "1171007024:AAGxwY_kQ0w2lpG1KrVutwY6P5n_fDQQoVs"
html = 'https://cfo.zol.ru/?sell=on&buy=on&without_exact_fo=On&buy=On&sell=On&buy_other=Off&sell_other=Off&other=Off&nearby_regions=Off&nearby_countries=Off&without_exact_fo=On&'

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
    def text_of_ad(self):
        html_for_parse_2 = requests.get(self.html).content
        soup_2 = BeautifulSoup(html_for_parse_2)
        raw_html_2 = soup_2.select('#table_offers')[0]
        raw_html_2 = raw_html_2.find_all('table')
        link = raw_html_2[0].find('a').get('href')
        html_for_further_parse = requests.get(link).content
        text_ad = BeautifulSoup(html_for_further_parse).body.find_all(class_ = 'col-12 news-body')[0].get_text().replace('\r', '')
        text_ad = text_ad.replace('\n', '')
        text_ad = text_ad.replace('Сообщение автору объявленияОтправитьДля получения обратной связи, пожалуйста, заполните следующую формуВаше имяВаш E-mailВаш пароль:ОтправитьДля удобства отправки сообщений рекомендуется предварительно авторизироваться на сайте, в этом случае не будет необходимости в заполнении данной формы.                                     Если Вы еще не зарегистрированы на сайте, пожалуйста, зарегистрируйтесь.','')
        text_ad = re.sub(' +', ' ', text_ad)
        text_ad = text_ad.replace('\xa0', '')
        return text_ad
        
    
ZernoCheckerBot = BotHandler(token)


# In[ ]:


ZernoCheckerBot = BotHandler(token)
def main():
    new_offset = None
    site_last_upd = ZernoCheckerBot.final_table().iloc[0,:]
    all_chat_ids = ['252157295','330165478','893215787']
    while True:
        ZernoCheckerBot.get_updates(new_offset)
        last_update = ZernoCheckerBot.get_last_update()
        if last_update == None: continue
        last_update_id = last_update['update_id']
        last_chat_id = last_update['message']['chat']['id']
        last_chat_name = last_update['message']['chat']['first_name']
        last_chat_text = last_update['message']['text']
        if ZernoCheckerBot.final_table().iloc[0,:].equals(site_last_upd) == False:
            for i in all_chat_ids:
                ZernoCheckerBot.send_message(i, ZernoCheckerBot.text_of_ad() )
                time.sleep(3)
                ZernoCheckerBot.send_message(i, ZernoCheckerBot.details() )
                site_last_upd = ZernoCheckerBot.final_table().iloc[0,:]
        if last_chat_text.lower() == 'ты работаешь?':
            ZernoCheckerBot.send_message(last_chat_id, 'Да')
            continue
        if last_chat_text.lower() == 'время':
            ZernoCheckerBot.send_message(last_chat_id, datetime.now().strftime('%H:%M:%S') ) 
            continue

if __name__ == '__main__':  
    try:
        main()
    except KeyboardInterrupt:
        exit() 


# In[131]:


# my chat id = '252157295'
# Papa chat id = '330165478'
# Dydya Andrei = '893215787'

