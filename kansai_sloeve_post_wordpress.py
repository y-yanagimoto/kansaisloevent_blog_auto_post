
import PySimpleGUI as sg
import requests
from time import sleep
import pandas as pd
import unicodedata
import string
import urllib
import os
from wordpress_xmlrpc.methods import media, posts
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from PIL import Image, ImageFilter,ImageFont,ImageDraw
#③実行する
import gspread
import json
import glob
import shutil
#ServiceAccountCredentials：Googleの各サービスへアクセスできるservice変数を生成します。
from oauth2client.service_account import ServiceAccountCredentials 
from gspread_dataframe import get_as_dataframe, set_with_dataframe
#2つのAPIを記述しないとリフレッシュトークンを3600秒毎に発行し続けなければならない
import ssl
from datetime import datetime as dt
ssl._create_default_https_context = ssl._create_unverified_context
from wordpress_xmlrpc import Client, WordPressPost
from wordpress_xmlrpc.methods.users import GetUserInfo
from wordpress_xmlrpc.methods.posts import GetPosts, NewPost
# from utils import *
import datetime
import time
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.events import EventFiringWebDriver, AbstractEventListener

def upload_image(in_image_file_name, out_image_file_name):
    if os.path.exists(in_image_file_name):
        with open(in_image_file_name, 'rb') as f:
            binary = f.read()

        data = {
            "name": out_image_file_name,
            "type": 'image/png',
            "overwrite": True,
            "bits": binary
        }

        media_id = wp.call(media.UploadFile(data))['id']
        print(in_image_file_name.split('/')
              [-1], 'Upload Success : id=%s' % media_id)
        return media_id
    else:
        print(in_image_file_name.split('/')[-1], 'NO IMAGE!!')

#upload_image(upload_image_path,f'completed_image_{value["-text_date-"]}-{value["-tenpo_name-"]}_{target_num}.png')

def get_concat_h_multi_resize(im_list, resample=Image.BICUBIC):
    min_height = min(im.height for im in im_list)
    im_list_resize = [im.resize((int(im.width * min_height / im.height), min_height),resample=resample)
                    for im in im_list]
    total_width = sum(im.width for im in im_list_resize)
    dst = Image.new('RGB', (total_width, min_height))
    pos_x = 0
    for im in im_list_resize:
        dst.paste(im, (pos_x, 0))
        pos_x += im.width
    return dst

def get_concat_v_multi_resize(im_list, resample=Image.BICUBIC):
    min_width = min(im.width for im in im_list)
    im_list_resize = [im.resize((min_width, int(im.height * min_width / im.width)),resample=resample)
                    for im in im_list]
    total_height = sum(im.height for im in im_list_resize)
    dst = Image.new('RGB', (min_width, total_height))
    pos_y = 0
    for im in im_list_resize:
        dst.paste(im, (0, pos_y))
        pos_y += im.height
    return dst

def generate_pickup_slump_graphe_image(im_list,value,target_num):
    global upload_image_path
    print('im_listの長さ',len(im_list))
    upload_image_path =f'temp/completed_image_{value["-text_date-"]}-{value["-tenpo_name-"]}_{target_num}.png'
    if len(im_list) <= 4:
        get_concat_h_multi_resize(im_list).save(upload_image_path)

    elif 4 < len(im_list) <= 8:
        get_concat_h_multi_resize(im_list[:4]).save('temp/h_concat_1.png')
        im = Image.open('image/white.png')
        while True:
            im_list.append(im)
            if len(im_list) == 8:
                break
        get_concat_h_multi_resize(im_list[4:]).save('temp/h_concat_2.png')
        
        im1 = Image.open('temp/h_concat_1.png')
        im2 = Image.open('temp/h_concat_2.png')
        get_concat_v_multi_resize([im1,im2]).save(upload_image_path)

    elif 8 < len(im_list) <= 12:
        get_concat_h_multi_resize(im_list[:4]).save('temp/h_concat_1.png')
        get_concat_h_multi_resize(im_list[4:8]).save('temp/h_concat_2.png')
        im = Image.open('image/white.png')
        while True:
            im_list.append(im)
            if len(im_list) >= 12:
                break
        get_concat_h_multi_resize(im_list[8:]).save('temp/h_concat_3.png')
        im1 = Image.open('temp/h_concat_1.png')
        im2 = Image.open('temp/h_concat_2.png')
        im3 = Image.open('temp/h_concat_3.png')
        get_concat_v_multi_resize([im1,im2,im3]).save(upload_image_path)

    elif 12 < len(im_list) <= 16:
        get_concat_h_multi_resize(im_list[:4]).save('temp/h_concat_1.png')
        get_concat_h_multi_resize(im_list[4:8]).save('temp/h_concat_2.png')
        get_concat_h_multi_resize(im_list[8:12]).save('temp/h_concat_3.png')
        im = Image.open('image/white.png')
        while True:
            im_list.append(im)
            if len(im_list) >= 16:
                break
        get_concat_h_multi_resize(im_list[12:]).save('temp/h_concat_4.png')
        im1 = Image.open('temp/h_concat_1.png')
        im2 = Image.open('temp/h_concat_2.png')
        im3 = Image.open('temp/h_concat_3.png')
        im4 = Image.open('temp/h_concat_4.png')
        get_concat_v_multi_resize([im1,im2,im3,im4]).save(upload_image_path)
    else:
        print('パスしました')
        pass
    return upload_image_path


def resize_image(image_path):
    conpleted_im = Image.open(image_path)
    # サイズを幅と高さにアンパック
    width, height = conpleted_im.size
    print(width,height)
    # 矩形の幅と画像の幅の比率を計算
    x_ratio = width / conpleted_im.height
    print(x_ratio)

    # リサイズ後の画像サイズにリサイズ
    resized_image = conpleted_im.resize((920,int(920/x_ratio)),resample=Image.LANCZOS)
    resized_image.save(image_path)

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

def get_selenium_tenpo_data(value):
    global prefecture
    options = Options()
    options.add_argument('--headless')
    browser = webdriver.Chrome(ChromeDriverManager().install(),options=options)
    tenpo_name = value['-tenpo_name-']
    url = f"https://ana-slo.com/{value['-text_date-']}-{value['-tenpo_name-']}-data/"
    print(url)
    print('データ取得中...30秒ほど時間がかかります。')
    browser.get(url)
    html = browser.page_source.encode('utf-8')
    dfs = pd.read_html(html)
    #display(tenpo_df)
    time.sleep(1)
    elements = browser.find_element(By.CLASS_NAME, 'st-catgroup')
    prefecture = elements.text.split(' ')[-1]
    for df in  dfs:
    #print(df.columns)
        if '機種名' in list(df.columns):
            ichiran_df = df
            ichiran_df['店舗名'] = tenpo_name
            #ichiran_df['都道府県'] = prefecture
            ichiran_df['機種名'] = ichiran_df['機種名'].map(removal_text)
            first_column = ichiran_df.pop('店舗名')
            ichiran_df.insert(0,'店舗名',first_column)
            break
    tenpo_day_data_df = ichiran_df
    tenpo_day_data_df = tenpo_day_data_df.sort_values('台番号')
    return tenpo_day_data_df

def write_dataframe_to_spreadsheet(write_spreadsheet_df,value):
    global worksheet,worksheet2,workbook
    scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']

    #認証情報設定
    #ダウンロードしたjsonファイル名をクレデンシャル変数に設定（秘密鍵、Pythonファイルから読み込みしやすい位置に置く）
    from pathlib import Path

    data_json = Path('data_json.json')
    data_json.write_text(r'''{
    "type": "service_account",
    "project_id": "twitteranalytics-291003",
    "private_key_id": "f2faf10b2e1d6aa58cc8939dd2cdbfcedca21af9",
    "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvAIBADANBgkqhkiG9w0BAQEFAASCBKYwggSiAgEAAoIBAQC1nD67P3TzaHsH\nwb+Im2P6Fs7yFrYcWUWS5/OF9SEUhedNzrOFhiVvorrRSTK1CHgZaOI57g0OPKJy\nuX3xqFyIh8SKhODGX4EKJt2MBTMPhiKwNMaXXjPtLotZjtFMF7ymPbR641QmXofH\nhc2x0g05gq2ZbIBqPZ6NWWm/ZhCsSG/alhnB8pGMwOAAB7zInfXgCsYcLeHXSWEM\npsTkU6fy46BK+I+skNPpnIjGgop8zgf3uo1AEO2/q9VcHZDvlO1rKjRJNa038XLq\nDPshEcklRgzQUgxSMQQcNHfAFADMlkPqlq1V0GRPE0/gn0rVIbEV7PNxsp4iVBMs\nxET3hpaZAgMBAAECggEABqMGG9uuz3JjBJ6M/FYJaktJFsnDr/eHNl4ppRyXL+PQ\n1yQVpWyIk7LTtvBA3SLJGMyfb9SGP53xpdWnh5xKfWbQxOskN7unwJI5CHPsMMYL\nIHtdQozbwvAvgX9ZoLlBWKXqoY8LNTfBKIZ4ROZTO2XOKEwxyTAlSi8ZUThOpa0U\nE93a1V8QiXvPbUMZRMWLT5bRN8mspgOBED6CkwrLV72JGrhIMxk8W/ZIsJ7beb2q\njgYhCY/c/7PTGD72RaL6oRIexYVSS08s6aveBqA+mD+Ey7/0HEQwpeSEU3DcyyWp\nYwoImEt0JO0xiSX0XMeI4C/zp5I6sJstlOTm8Cl4fQKBgQD5f7AfR0aWjO+9/St+\n0RKE5EiYzufI9AFI1zAFyIpyjkjoOAq4EvEae8I5EF103BReOS2bqAIkilUZ18O6\nYXW52lXq1mjNSQ3kk3cbV19rQ9KB90w0Qw9uhdIXwNSxZvCZ6I9ieWkgT8fVz5xs\nc+AkJZr6/5jqdQrqVsCerso3hwKBgQC6V7Lq2WL8HdDSXvFZc45s6Ep7RDMhlEYp\njUP+U/hpms9unRh/6P8FTKX5CNGX+AnnxfWwUU7AtCDhxp3Drbv6zVr7/fXVSKAx\nJadUWfftmBz1ESqg/NIsuFuCvZjbveOaU8D/k2SL5KSuFcTReYfrrCSqkwjkb5/v\nAEptoDwI3wKBgEk/G02Tdz2rkpaMRMCuUGmDO2zhEVsFh3sC8a5A+aQ38V97VGpF\n5VKJErP+AfHUyoX+80zHPhnMIr+7gFKvWgh9+MtAtvPNhq6cPFNiizjKaHqPR2fw\naA9iahNfIRITzn7gr3eRfTNnOJukn5+XRS5Xe/BEKXhrdBDn9xSe6+7xAoGAJrEf\nDXSmAQOP4J6mLpS39hUlogK/OzG2f9o9TAnTgtoKSEWGWMjgaxFHRTZ3jr6KD/4i\nzcGUQJ8mVLsQ9xiT97e8NKa+7NJvsMTIwdMMj+EN4jT2TQcx/Ocq2TLVEouTPvA1\nGtxX/FQ1fZA3ledOObk8w85UAlrLMq00xx6GWLECgYB1MCU2wezNiDidNNxJsYJS\nXzPpOCmaHwFfl3cE/aixoWTHSSQ1KyfQKZB8zp5GeaJ29wbrH89sk+op1inoa17k\nU3NSuamn4KTrm9G9DYiDzxA3G3GD1t8RiGrIGzDeV+Czcfbc619bwia9fDACNMKa\nvh1DZj8GBp9bPsFUpM35Xw==\n-----END PRIVATE KEY-----\n",
    "client_email": "twittersheets@twitteranalytics-291003.iam.gserviceaccount.com",
    "client_id": "103017426237885232380",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/twittersheets%40twitteranalytics-291003.iam.gserviceaccount.com"
    }''', encoding='utf-8')  # 書き込み!
    
    scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']

    #認証情報設定
    #ダウンロードしたjsonファイル名をクレデンシャル変数に設定（秘密鍵、Pythonファイルから読み込みしやすい位置に置く）
    credentials = ServiceAccountCredentials.from_json_keyfile_name(data_json, scope)
    gc = gspread.authorize(credentials)
    workbook = gc.open_by_url('https://docs.google.com/spreadsheets/d/1zcz0DpjgCk1_h3pX7CFD7LkxRfLi3YCy1KnCHOJzpeI/edit#gid=734960479')
    

    title_text = value['-tenpo_name-'] + '_'+ value['-text_date-']
    workbook.add_worksheet(title=title_text, rows=len(tenpo_day_data_df)+1, cols=14)
    worksheet = workbook.worksheet(title_text)
    #df_a['G数'] = df_a['G数'].map(set_round)

    sum_append_list = []
    write_spreadsheet_df['差枚'] = pd.to_numeric(write_spreadsheet_df['差枚'], downcast='integer')
    write_spreadsheet_df['G数'] = pd.to_numeric(write_spreadsheet_df['G数'], downcast='integer')
    write_spreadsheet_df = write_spreadsheet_df.reset_index(drop=True)
    for i in range(0,len(write_spreadsheet_df)):
        #print(write_spreadsheet_df[i:i+6].sum()['差枚'])
        sum_append_list.append(write_spreadsheet_df[i:i+6].sum()['差枚'])
    write_spreadsheet_df['6行合計値'] = sum_append_list
    #display(write_spreadsheet_df.style.bar(align="mid",color=['#d65f5f', '#5fba7d']))
    #write_spreadsheet_df = write_spreadsheet_df.drop('6行合計値',axis=1)
    #ここで出ている箇所を確認する
    write_spreadsheet_df['対象'] = ''
    set_with_dataframe(worksheet, write_spreadsheet_df)

    kisyubetu_master_df = tenpo_day_data_df.groupby('機種名').sum()
    kisyubetu_master_df['総台数'] = tenpo_day_data_df.groupby('機種名').size()
    kisyubetu_master_df = kisyubetu_master_df.reset_index(drop=False).reset_index().rename(columns={'index': '機種順位','ゲーム数': 'G数'})
    kisyubetu_master_df['機種順位'] = kisyubetu_master_df['機種順位'] + 1
    kisyubetu_master_df[['機種順位','機種名','総台数','G数','差枚']]
    kisyubetu_win_daissuu_list = []
    kisyubetu_master_df_list = []
    for kisyu_name in kisyubetu_master_df['機種名']:
        kisyu_df = tenpo_day_data_df.query('機種名 == @kisyu_name')
        kisyubetu_master_df_list.append(kisyu_df)
        kisyu_win_daisuu = len(kisyu_df[kisyu_df['差枚'] > 0])
        kisyubetu_win_daissuu_list.append(kisyu_win_daisuu)

    kisyubetu_master_df['勝率'] = kisyubetu_win_daissuu_list
    kisyubetu_master_df['勝率'] = kisyubetu_master_df['勝率'].astype(str)
    kisyubetu_master_df['総台数'] = kisyubetu_master_df['総台数'].astype(int)
    kisyubetu_master_df['平均G数'] = kisyubetu_master_df['G数'] / kisyubetu_master_df['総台数'] 
    kisyubetu_master_df['平均G数'] = kisyubetu_master_df['平均G数'].astype(int)
    kisyubetu_master_df = kisyubetu_master_df[kisyubetu_master_df['総台数'] >= 2 ]
    kisyubetu_master_df['差枚'] = kisyubetu_master_df['差枚'].astype(int)
    kisyubetu_master_df['平均差枚'] = kisyubetu_master_df['差枚'] / kisyubetu_master_df['総台数'] 
    kisyubetu_master_df['平均差枚'] = kisyubetu_master_df['平均差枚'].astype(int)
    kisyubetu_master_df['総台数'] = kisyubetu_master_df['総台数'].astype(str)
    kisyubetu_master_df['勝率'] = kisyubetu_master_df['勝率'] + '/' + kisyubetu_master_df['総台数']
    kisyubetu_master_df['勝率'] = kisyubetu_master_df['勝率'].map(lambda x : '(' + x + '台) ' + str(round(int(x.split('/')[0])/int(x.split('/')[1])*100,1))  + '%')
    kisyubetu_master_df = kisyubetu_master_df[['機種順位','機種名','勝率','総台数','G数','平均G数','差枚','平均差枚']]
    kisyubetu_master_df = kisyubetu_master_df.sort_values('平均差枚',ascending=False)
    kisyubetu_master_df['機種順位'] = list(range(1,len(kisyubetu_master_df)+1))
    kisyubetu_master_df['機種平均出率'] =(((kisyubetu_master_df['G数'] * 3) + kisyubetu_master_df['差枚']) / (kisyubetu_master_df['G数'] * 3) )*100
    kisyubetu_master_df['機種平均出率'] = kisyubetu_master_df['機種平均出率'].map(lambda x : round(x,1))
    workbook.add_worksheet(title=title_text+'_機種別', rows=len(kisyubetu_master_df)+1, cols=len(kisyubetu_master_df.columns)+1)
    worksheet2 = workbook.worksheet(title_text+'_機種別')
    set_with_dataframe(worksheet2, kisyubetu_master_df)

def set_round_int(x):
    x = int(round(x, 0))
    return x
    
def post_wordpress(workbook,worksheet,value):
    global extract_read_worksheet_df,read_worksheet_df
    read_worksheet_df = pd.DataFrame(worksheet.get_all_values())
    read_worksheet_df.columns = list(read_worksheet_df.loc[0, :])
    read_worksheet_df.drop(0, inplace=True)
    pickup_df_text = ''
    
    options = Options()
    options.add_argument('--headless')
    browser = webdriver.Chrome(ChromeDriverManager().install(),options=options)

    url = f"https://ana-slo.com/{value['-text_date-']}-{value['-tenpo_name-']}-data/"
    print(url)
    print('データ取得中...30秒ほど時間がかかります。')
    browser.get(url)
    html = browser.page_source.encode('utf-8')
    dfs = pd.read_html(html)
    #display(tenpo_df)
    time.sleep(1)
    elements = browser.find_element(By.CLASS_NAME, 'st-catgroup')
    prefecture = elements.text.split(' ')[-1]
    tab_element_list :list = browser.find_elements_by_class_name('tab-menu_item')

    class CustomListener(AbstractEventListener):
        def before_click(self, element,browser):
            # 要素までスクロールさせる
            browser.execute_script('arguments[0].scrollIntoView({behavior: "smooth", block: "start"});', element)

    for i,element in enumerate(tab_element_list):
        print(i)
        if i % 2 != 0:
            element.click()
            browser.implicitly_wait(2)
        else:
            pass
            #print(i)

        
    pickup_df_text = ''
    for target_num in read_worksheet_df['対象'].unique():
        target_dir = 'temp'
        
        os.mkdir(target_dir)

        if target_num == '':
            print('continue')
            continue
        extract_read_worksheet_df = read_worksheet_df.query('対象.str.contains(@target_num)', engine='python')
        #read_worksheet_df = read_worksheet_df.drop("対象", axis=1)
        
        extract_read_worksheet_df = extract_read_worksheet_df[['機種名','台番号','G数','差枚','BB','RB','合成確率']]
        for dai_number in  extract_read_worksheet_df['台番号']:
            element = browser.find_element_by_id(str(dai_number))
            scroll = CustomListener()
            scroll.before_click(element,browser)
            time.sleep(1)
            browser.implicitly_wait(2)
            parents_element = element.find_element_by_xpath('..')

            png = parents_element.screenshot_as_png
            # ファイルに保存
            with open(f'temp/{dai_number}.png', 'wb') as f:
                f.write(png)

        files = glob.glob("temp/*")
        im_list = []

        for file in files:
            print(file)
            im = Image.open(file)
            w, h = im.size
            draw = ImageDraw.Draw(im)
            draw.rectangle((0, 0, w-1, h-1), outline = (255,255,255))
            im.save(file)
            im_list.append(im)
        print(im_list)
        upload_image_path = generate_pickup_slump_graphe_image(im_list,value,target_num)
        output_path = f'completed_image_{value["-text_date-"]}-{value["-tenpo_name-"]}_{target_num}.png'
        resize_image(upload_image_path)
        upload_image(upload_image_path,output_path)
        pickup_df_text +=  '<div class="table-wrap">' + extract_read_worksheet_df.to_html(justify='justify-all',index=False) + '</div>'
        url = f'<a href=http://kansai-sloeve.com/wp-content/uploads/{today.strftime("%Y/%m")}/{output_path}">\n<img src="http://kansai-sloeve.com/wp-content/uploads/{today.strftime("%Y/%m")}/{output_path}" alt="{value["-text_date-"]}-{value["-tenpo_name-"]}_{target_num}" class="alignnone size-full " /></a>'
        pickup_df_text += '\n' + url + '\n'
        shutil.rmtree(target_dir)
    
    pickup_text = '<h2>注目ピックアップ</h2>\n[st-kaiwa1]今回の並びでよかった場所がこちら[/st-kaiwa1]'
    
    pickup_text_2 = '\n[st-kaiwa1]今回の並びの一言コメントを記入[/st-kaiwa1]'

    kisyubetu_master_df = tenpo_day_data_df.groupby('機種名').sum()
    kisyubetu_master_df['総台数'] = tenpo_day_data_df.groupby('機種名').size()
    kisyubetu_master_df = kisyubetu_master_df.reset_index(drop=False).reset_index().rename(columns={'index': '機種順位','ゲーム数': 'G数'})
    kisyubetu_master_df['機種順位'] = kisyubetu_master_df['機種順位'] + 1
    kisyubetu_master_df[['機種順位','機種名','総台数','G数','差枚']]
    kisyubetu_win_daissuu_list = []
    kisyubetu_master_df_list = []
    for kisyu_name in kisyubetu_master_df['機種名']:
        kisyu_df = tenpo_day_data_df.query('機種名 == @kisyu_name')
        kisyubetu_master_df_list.append(kisyu_df)
        kisyu_win_daisuu = len(kisyu_df[kisyu_df['差枚'] > 0])
        kisyubetu_win_daissuu_list.append(kisyu_win_daisuu)
    kisyubetu_master_df['勝率'] = kisyubetu_win_daissuu_list
    kisyubetu_master_df['勝率'] = kisyubetu_master_df['勝率'].astype(str)
    kisyubetu_master_df['総台数'] = kisyubetu_master_df['総台数'].astype(int)
    kisyubetu_master_df['平均G数'] = kisyubetu_master_df['G数'] / kisyubetu_master_df['総台数'] 
    kisyubetu_master_df['平均G数'] = kisyubetu_master_df['平均G数'].astype(int)
    kisyubetu_master_df = kisyubetu_master_df[kisyubetu_master_df['総台数'] >= 2 ]
    kisyubetu_master_df['差枚'] = kisyubetu_master_df['差枚'].astype(int)
    kisyubetu_master_df['平均差枚'] = kisyubetu_master_df['差枚'] / kisyubetu_master_df['総台数'] 
    kisyubetu_master_df['平均差枚'] = kisyubetu_master_df['平均差枚'].astype(int)
    kisyubetu_master_df['総台数'] = kisyubetu_master_df['総台数'].astype(str)
    kisyubetu_master_df['勝率'] = kisyubetu_master_df['勝率'] + '/' + kisyubetu_master_df['総台数']
    kisyubetu_master_df['勝率'] = kisyubetu_master_df['勝率'].map(lambda x : '(' + x + '台) ' + str(round(int(x.split('/')[0])/int(x.split('/')[1])*100,1))  + '%')
    kisyubetu_master_df = kisyubetu_master_df[['機種順位','機種名','勝率','総台数','G数','平均G数','差枚','平均差枚']]
    kisyubetu_master_df = kisyubetu_master_df.sort_values('平均差枚',ascending=False)
    kisyubetu_master_df['機種順位'] = list(range(1,len(kisyubetu_master_df)+1))
    kisyubetu_master_df['機種平均出率'] =(((kisyubetu_master_df['G数'] * 3) + kisyubetu_master_df['差枚']) / (kisyubetu_master_df['G数'] * 3) )*100
    kisyubetu_master_df['機種平均出率'] = kisyubetu_master_df['機種平均出率'].map(lambda x : round(x,1))
    title_text = value['-tenpo_name-'] + '_'+ value['-text_date-']
    #workbook.add_worksheet(title=title_text+'_機種別', rows=len(kisyubetu_master_df)+1, cols=len(kisyubetu_master_df.columns)+1)
    #worksheet = workbook.worksheet(title_text+'_機種別')
    #set_with_dataframe(worksheet, kisyubetu_master_df)

#html出力用


    from datetime import datetime as dt
    
    tdatetime = dt.strptime(value['-text_date-'], '%Y-%m-%d')
    month = tdatetime.strftime('%m').lstrip('0')
    day = tdatetime.strftime('%d').lstrip('0')
    date_str = month + '/' + day 
    #タイトル部分の出力
    print(value)
    day_number = value['-text_date-'][-1]
    tenpo_name = value['-tenpo_name-']
    print(tenpo_name)
    title = '<h2>' + date_str + ' ' + tenpo_name + ' 結果</h2>'

    tenpo_ave_gamesuu = int(tenpo_day_data_df['G数'].sum() / len(tenpo_day_data_df['G数']))
    tenpo_ave_gamesuu = str("{:,}".format(tenpo_ave_gamesuu)) + 'G'
    tenpo_ave_samai = str(int(tenpo_day_data_df['差枚'].sum() / len(tenpo_day_data_df['G数']))) + '枚'
    tenpo_sousamai = tenpo_day_data_df['差枚'].sum()
    tenpo_sousamai = str("{:,}".format(tenpo_sousamai )) + '枚'

    win_rate_bunshi = 0
    for x in list(tenpo_day_data_df['差枚']):
        if x > 0:
            win_rate_bunshi += 1
        else:
            pass
    win_rate = str(win_rate_bunshi)+'/'+str(len(tenpo_day_data_df['G数']))

    #概要部分の出力
    tenpo_gaiyou_dict = {'状況': ['総差枚', '平均差枚', '平均G数', '勝率'], f'旧イベント日（{day_number}のつく日）':[tenpo_sousamai,tenpo_ave_samai, tenpo_ave_gamesuu, win_rate]}

    matome_df = pd.DataFrame.from_dict(tenpo_gaiyou_dict)

    gaiyou_matome = matome_df.to_html(justify='justify-all',index=False)
    #print(gaiyou_matome)

    #機種の全台データ一覧
    #print(ichiran_df.to_html(justify='justify-all',index=False))
    write_ichiran_df = read_worksheet_df[['機種名','台番号','G数','差枚','BB','RB','合成確率']]
    text = write_ichiran_df.to_html(justify='justify-all',index=False)
    completed_text ='[su_spoiler title="全台データ一覧" style="fancy" icon="chevron-circle" anchor="Hello"]' +'<div class="table-wrap">' + text +'</div>' + '[/su_spoiler]'

    #差枚G数グラフ一覧
    #kisyubetu_master_df = pd.read_html(url)[1]

    horaizontal_bar_graph = """<script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/2.1.4/Chart.min.js"></script>
    <canvas id="myChart" height="1500" style="padding: 0px 10px 0px 10px;"></canvas>
    <script>
    var ctx = document.getElementById("myChart").getContext('2d');
    var myChart = new Chart(ctx, {
    type: 'horizontalBar',
    data:  {
        labels:""" + str(kisyubetu_master_df['機種名'].to_list()) + """,
        datasets: [{
            label: "平均差枚",
            data:""" + str(kisyubetu_master_df['差枚'].to_list()) +""",
            borderColor: "rgb(255, 99, 132)",
            backgroundColor: "red"
        },{
            label: "平均G数",
            data:""" + str(kisyubetu_master_df['G数'].to_list()) + """,
    backgroundColor: "blue"
        }
    ]
    }
    });
    </script>"""
    #print(horaizontal_bar_graph)

    kisyu_matome_text = ''
    #機種名別テーブル
    #kisyubetu_master_df = pd.read_html(url)[1]

    for kisyu_name in kisyubetu_master_df['機種名']:
        target_matome_kisyu = kisyubetu_master_df[kisyubetu_master_df['機種名'] == kisyu_name]
        try:
            kisyu_text = f'{str(target_matome_kisyu.iloc[0,1])}<br> 平均差枚:{str(target_matome_kisyu.iloc[0,7])}枚<br> 平均G数:{str(target_matome_kisyu.iloc[0,5])}G<br>  勝率:{str(target_matome_kisyu.iloc[0,2])}<br>  平均出率:{str(target_matome_kisyu.iloc[0,8])}'
        except:
            continue
        kisyu_matome_text += '[su_spoiler title="'   + kisyu_text + '" style="fancy" icon="chevron-circle" anchor="Hello"]'  + '<div class="table-wrap">'
        #print('[su_spoiler title="',kisyu_text,'" style="fancy" icon="chevron-circle"]')
        
        target_kisyu = read_worksheet_df.query(f'機種名.str.contains("{kisyu_name}")', engine='python')
        target_kisyu['差枚'] = target_kisyu['差枚'].astype(str) + '枚'
        target_kisyu['G数'] = target_kisyu['G数'].astype(str) + 'G'
        target_kisyu = target_kisyu[['機種名','台番号','G数','差枚','BB','RB','合成確率']]
        kisyu_matome_text += target_kisyu.to_html(justify='justify-all',index=False) + '\n'
        #print(target_kisyu.to_html(justify='justify-all',index=False))
        
        kisyu_matome_text += '</div>' + '[/su_spoiler]' + '\n'
        #print('[/su_spoiler]')


    zizen_text = '\n<h2>事前情報</h2>\n画像を入れてください\n[st-kaiwa1]一言コメント部分[/st-kaiwa1]'

    full_text  = (title + '\n' + gaiyou_matome + zizen_text +  pickup_text + pickup_df_text + pickup_text_2 + "<h2>全台データ一覧</h2>※タップで一覧が開きます"+ completed_text + '<h2>機種別データ一覧</h2>※機種タップで各台データが見れます' + kisyu_matome_text)
    #horaizontal_bar_graph +
    print('準備完了')

    # -*- coding: utf-8 -*-

    def main():
        global wp
        """
        変数を定義
        """
        id = "admin"
        password="slopachi777"
        #idとpasswordはwordpressの管理画面に入るためのもの

        url="https://kansai-sloeve.com/xmlrpc.php"
        #第3者が閲覧するURLの後ろに/xmlrpc.phpをつける。
        #ワードプレスの管理画面の後ろにつけるとエラーになった

        which="draft"
        #which="draft"
        #下書きに投稿するか本番で投稿するか選択
        """
        クライアントの呼び出しなど
        """

        wp = Client(url, id,password)
        post = WordPressPost()

        """
        実際に投稿する
        """

        post.post_status = which
        post.title = date_str +' '+tenpo_name + '結果まとめ'
        post.content = full_text
        post.terms_names = {
        "post_tag": [f'{day_number}のつく日',tenpo_name,prefecture],
        "category": ['結果記事'],
        }
        #過去に投稿した記事としたい場合、投稿日をここで指定。例として2018年1月1日10時5分10秒に投稿した例を示す。
        #post.date=datetime.strptime("2018/1/01 10:05:10","%Y/%m/%d %H:%M:%S")
        wp.call(NewPost(post))

    main()



id = "admin"
password="slopachi777"
#idとpasswordはwordpressの管理画面に入るためのもの

url="https://kansai-sloeve.com/xmlrpc.php"
#第3者が閲覧するURLの後ろに/xmlrpc.phpをつける。
#ワードプレスの管理画面の後ろにつけるとエラーになった
today = datetime.date.today()

wp = Client(url, id,password)

yesterday = datetime.date.today() + datetime.timedelta(days=-1)

layout = [ 
    [sg.Text('読み取り対象の店舗名と日付けを指定してください')  ],
    [sg.Text("店舗名入力欄"), sg.Input(default_text='123笹塚店', key="-tenpo_name-")],
    [sg.Input(key='-text_date-', size=(30,1)),sg.CalendarButton('日付選択',format='%Y-%m-%d',default_date_m_d_y=(yesterday.month, yesterday.day, yesterday.year),locale='ja_JP', key='-button_calendar-',target='-text_date-')],
    [sg.Button('OK', key='-OK-'), sg.Cancel()],
    [sg.Output(size=(50, 5))]]

          # 'Submit', 'Cancel'というテキストのButtonが標準で用意されています。

window = sg.Window('関西スロイベ生成君', layout=layout)

while True:

    event, value = window.read()

    # eventに代入されているkeyに応じて処理を振り分けていく
    if event in [None, 'Cancel']:
        break
    
    elif event == '-OK-':
        print('処理を実行中です...')
        tenpo_day_data_df = get_selenium_tenpo_data(value)
        print(value)
        print(value['-text_date-'])
        
        write_dataframe_to_spreadsheet(tenpo_day_data_df,value)
        pressed_text = sg.popup_yes_no("スプレッドシートへの書き込みが完了しました。\n抜き出し箇所の処理が終わったらyesを押してください")

        
        if pressed_text == "Yes":
            #start_app()
            print('記事投稿開始')
            post_wordpress(workbook,worksheet,value)
            sg.popup('下書きに投稿しました')
            #workbook.del_worksheet(worksheet)
            #workbook.del_worksheet(worksheet2)

window.close()
#tenpo_day_data_df