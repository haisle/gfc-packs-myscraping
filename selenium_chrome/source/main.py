import os
from selenium import webdriver
import requests
from bs4 import BeautifulSoup
import re
from google.cloud import storage

def scrapisecondps(data, context):

    chrome_options = webdriver.ChromeOptions()
    
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--window-size=1280x1696')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--hide-scrollbars')
    chrome_options.add_argument('--enable-logging')
    chrome_options.add_argument('--log-level=0')
    chrome_options.add_argument('--v=99')
    chrome_options.add_argument('--single-process')
    chrome_options.add_argument('--ignore-certificate-errors')
    chrome_options.binary_location = os.getcwd() + "/headless-chromium"    
    
    # open selenium browser with headless
    driver = webdriver.Chrome(os.getcwd() + "/chromedriver",chrome_options=chrome_options)
    driver.get("https://*********.co.jp/auth/login")
    # input login id
    login_id = driver.find_element_by_name("data[User][username]")
    login_id.send_keys("***your_id is here***")
    # input password
    password = driver.find_element_by_name("data[User][password]")
    password.send_keys("*** your_pass is here***")
    # click the login button
    login_btn = driver.find_element_by_xpath('//*[@id="AuthGeneral"]/div[2]/button')
    login_btn.click()
    # target webpage
    driver.get("https://**********.co.jp/***********")
    #get source
    html = driver.page_source.encode('utf-8')
    bs = BeautifulSoup(html, "html.parser")
    
    # finish selenium browser
    driver.close()
    driver.quit()
    
    # scraping the contents
    elems = bs.find_all(href=re.compile("blog_entries/view"))
    elems_today = elems[0].contents[0]
    elems_yesterday = elems[1].contents[0]
        
    # scraping the date
    date_info = bs.find_all(attrs={'class':'blogs_entry_meta'})
    date_info_latest = date_info[0]
    date_info_extract = date_info_latest.find(string=re.compile('***keyword which you want***'))
    date_info_reshape  = date_info_extract.split()
    date_info_fin = date_info_reshape[0] + date_info_reshape[2]

    # contents shaping
    new_list = elems_today + elems_yesterday
    new_list_bin = new_list.encode('utf-8')

    # google storage
    bucket_name = '***your bucket id is here***'
    blob_name = '***your blob id is here***.bin'
    
    # preparing api for google storage
    client = storage.Client()

    # prepairing blob for download old contents from google cloud
    bucket = client.get_bucket(bucket_name)
    blob = bucket.blob(blob_name)

    # download and assign value to old_list
    old_list_bin = blob.download_as_string()
    old_list = old_list_bin.decode('utf-8')
    
    # prepairing blob for upload new contents to google cloud
    # as you know, we have the same code above, I thought why I need the same code again, but in my case, we need twice, it is not work with one code.
    bucket = client.get_bucket(bucket_name)
    blob = bucket.blob(blob_name)

    # upload new content to google cloud
    blob.upload_from_string(new_list_bin)

    if old_list == new_list:
        # I have two tokens, if updated, the message will sent to the product thread, but if no updated, that will sent to the testing thread which receive only for developer (me). This method will help that developer can check the states that whether this program is work or not everyday, and customer will only receive this when contents was updated.
        line_notify_token = '***your line notify token (for "NO updated") is here***'
    else:
        line_notify_token = '***your line notify token (for "updated") is here***'
    
    # shape the message
    send_text = '***'
    
    # send the message to line
    line_notify_api = 'https://notify-api.line.me/api/notify'
    headers = {'Authorization': f'Bearer {line_notify_token}'}
    data = {'message': f"{send_text}"}
    requests.post(line_notify_api, headers = headers, data = data)
    # print(send_text)
    fin = "ok!"
    return fin
