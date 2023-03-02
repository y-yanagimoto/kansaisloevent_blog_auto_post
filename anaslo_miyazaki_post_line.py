import requests
from time import sleep
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import datetime
import time
import unicodedata
import string

def daisuu(field):
    field = int(field.split('/')[-1].replace(')',''))
    return field

def removal_text(text):
    text = unicodedata.normalize("NFKC", text)
    text = text.translate(str.maketrans( '', '',string.punctuation  + '！'+ '　'+ ' '+'・'+'～' + '‐'))
    return text

def post_line_text(message,token):
    url = "https://notify-api.line.me/api/notify"
    headers = {"Authorization" : "Bearer "+ token}
    payload = {"message" :  message}
    post = requests.post(url ,headers = headers ,params=payload) 

def post_line_text_and_image(message,image_path,token):
    url = "https://notify-api.line.me/api/notify"
    headers = {"Authorization" : "Bearer "+ token}
    payload = {"message" :  message}
    #imagesフォルダの中のgazo.jpg
    print('image_path',image_path)
    files = {"imageFile":open(image_path,'rb')}
    post = requests.post(url ,headers = headers ,params=payload,files=files) 


cols = ['機種名', '台番号', 'G数', '差枚', 'BB', 'RB', 'ART', 'BB確率', 'RB確率', 'ART確率','合成確率','店舗名']
ichiran_all_tennpo_df = pd.DataFrame(index=[], columns=cols)
prefecture = '宮崎県'
yesterday = datetime.date.today() + datetime.timedelta(days=-1)
options = Options()
options.add_argument('--blink-settings=imagesEnabled=false')
browser = webdriver.Chrome(ChromeDriverManager().install(),options=options)
url = f'https://ana-slo.com/%E3%83%9B%E3%83%BC%E3%83%AB%E3%83%87%E3%83%BC%E3%82%BF/{prefecture}/'
browser.get(url)
html = browser.page_source.encode('utf-8')
soup = BeautifulSoup(html, 'lxml')
tenpo_ichiran_df = pd.read_html(html)[-1]
#print(tenpo_ichiran_df['ホール名'])

i = 0
for tenpo_name in tenpo_ichiran_df['ホール名'] :#tenpo_ichiran_df['ホール名']
    try:
        url = f"https://ana-slo.com/{yesterday.strftime('%Y-%m-%d')}-{tenpo_name}-data/"
        browser.get(url)
        html = browser.page_source.encode('utf-8')
        dfs = pd.read_html(html)
        #display(tenpo_df)
        time.sleep(1)
        for df in  dfs:
        #print(df.columns)
            if '機種名' in list(df.columns):
                ichiran_df = df
                ichiran_df['店舗名'] = tenpo_name
                ichiran_df['機種名'] = ichiran_df['機種名'].map(removal_text)
                ichiran_all_tennpo_df =  pd.concat([ichiran_all_tennpo_df, ichiran_df])
                break
    except:
        time.sleep(1)
        continue
    i += 1
    # if i > 2:
    #     break

#post_line_text('処理おわり')
browser.quit()


#def generate_shizuoka_twitter_text(ichiran_all_tennpo_df,date):
tenpobetsu_df = ichiran_all_tennpo_df.groupby('店舗名').sum().sort_values('差枚',ascending=False)
daisuu_list = []
for tenpo_name in tenpobetsu_df.index:
    extract_df = ichiran_all_tennpo_df.query('店舗名 == @tenpo_name')
    #display(extract_df)
    daisuu:int = len(extract_df)
    daisuu_list.append(daisuu)
    
tenpobetsu_df['台数'] = daisuu_list
tenpobetsu_df['店舗平均差枚'] = tenpobetsu_df['差枚'] / tenpobetsu_df['台数'] 
tenpobetsu_heikinsamai_zyun_df = tenpobetsu_df.sort_values('店舗平均差枚',ascending=False)
tenpobetsu_heikinsamai_zyun_df.index



#def generate_shizuoka_twitter_text(ichiran_all_tennpo_df,date):
tenpobetsu_df = ichiran_all_tennpo_df.groupby('店舗名').sum().sort_values('差枚',ascending=False)
daisuu_list = []
for tenpo_name in tenpobetsu_df.index:
    extract_df = ichiran_all_tennpo_df.query('店舗名 == @tenpo_name')
    #display(extract_df)
    daisuu = len(extract_df)
    daisuu_list.append(daisuu)
    
tenpobetsu_df['台数'] = daisuu_list
tenpobetsu_df['店舗平均差枚'] = tenpobetsu_df['差枚'] / tenpobetsu_df['台数'] 
tenpobetsu_heikinsamai_zyun_df = tenpobetsu_df.sort_values('店舗平均差枚',ascending=False)
tenpobetsu_heikinsamai_zyun_df.index


date = yesterday
str_date =  date.strftime('%m').lstrip('0') + '月' + date.strftime('%d').lstrip('0')  +'日'
for i,tenpo_name in enumerate(tenpobetsu_heikinsamai_zyun_df.index):
    tenpo_ichiran_df = ichiran_all_tennpo_df.query('店舗名 ==@tenpo_name')
    tenpo_heikin_samai = int(tenpo_ichiran_df.sum()[3] / len(tenpo_ichiran_df))
    tenpo_name = tenpo_name.replace('本店','').replace('店','')
    tenpo_ichiran_df = tenpo_ichiran_df[tenpo_ichiran_df.duplicated(subset=['機種名'],keep=False)]
    kisyubetsu_df = tenpo_ichiran_df.groupby('機種名').sum().sort_values('差枚', ascending=False)
    text = f'\n\n🟠{str_date} {tenpo_name}'
    text_tenpmete = '''2月13日 ◯◯◯◯◯(店名)
平均＋〜枚（20スロ 〜台）

☀️シンフォ勇気 平均+2400枚
☀️ヴヴヴ 平均+1200枚
☀️バキ 平均+1000枚
※上位4機種
'''
    
    if tenpo_heikin_samai > 0:
        text += f"\n平均+{tenpo_heikin_samai}枚 (20スロ {len(tenpo_ichiran_df)}台)\n"
    else:
        text += f"\n平均{tenpo_heikin_samai}枚 (20スロ {len(tenpo_ichiran_df)}台)\n"
    print(text)

    daisuu_list = []

    for kisyu_name in kisyubetsu_df.index:
        extract_df = tenpo_ichiran_df[(tenpo_ichiran_df['機種名'] == kisyu_name)]
        #display(extract_df)
        if len(extract_df) == 0:
            print(kisyu_name)
            print(len(extract_df))
            daisuu = 1
            post_line_text(f'機種名がうまく抽出できませんでした\n{tenpo_name}\n{kisyu_name}','OYMi6gX1cC1QQthc4Q1dmpwmQ8I8Kbpdauq9txTr9Ci')

        else:
            daisuu = len(extract_df)
        daisuu_list.append(daisuu)


        
    kisyubetsu_df['台数'] = daisuu_list
    kisyubetsu_df['平均差枚'] = kisyubetsu_df['差枚'] / kisyubetsu_df['台数'] 
    kisyubetsu_df['平均差枚'] = kisyubetsu_df['平均差枚'].astype(int)

    #display(kisyubetsu_df)
    kisyubetsu_df = kisyubetsu_df.sort_values('平均差枚', ascending=False)
    for i,record in enumerate(kisyubetsu_df.itertuples()):
        win_daisuu = 0
        daisuu = 0
        extract_df = tenpo_ichiran_df[(tenpo_ichiran_df['機種名'] == record[0])]
        for dai_record in extract_df.itertuples():
            if dai_record[4] > 0:
                win_daisuu +=1
            else:
                pass
            daisuu += 1

        if int(record[13]) >= 0:
            text += '\n☀️' + record[0] + ' 平均+' + str(record[13]) + '枚'#+(' + str(win_daisuu)  +'/'+ str(daisuu)  + ')'
        else:
            text += '\n☀️' + record[0] + ' 平均' + str(record[13]) + '枚' #+ '('+ str(win_daisuu)  + '/' + str(daisuu)  + ')'

        if i == 3:
            break
    # if i < 5:
    #     post_line_text(f'{url}','94Fyb4vIQ3waJj11KO6e0oxZDJbv0pG7HD2x5gQlRp8')
    # else:
    #     pass
    post_line_text(f'{text}','OBi62mEP62iwRI3aRfXWFAyQjGggyvEzpWe8U4bxVBy')
    #break
    time.sleep(1)
