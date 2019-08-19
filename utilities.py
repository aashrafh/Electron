import os
import json
import pymongo
import urllib
from pathlib import Path
from config import *
from math import ceil
from time import sleep
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.common.exceptions import NoSuchElementException

client = pymongo.MongoClient("")
db = client.test

current_path=""
try:
    current_path = os.path.dirname(os.path.abspath(__file__))
except:
    current_path = '.'
    
def ini_driver(gecko_driver='', load_images=True, user_agent='', is_headless=False):
    firefox_profile=webdriver.FirefoxProfile()
    
    firefox_profile.set_preference('dom.ipc.plugins.enabled.libflashplayer.so', False)
    firefox_profile.set_preference('media.volume_scale', '0.0')
    firefox_profile.set_preference('dom.webnotifications.enabled', False)
    
    if not load_images:
        firefox_profile.set_preference('permissions.default.image', 2)
    if user_agent != "":
        firefox_profile.set_preference('general.useragent.override', user_agent)
    
    options = Options()
    #options.headless = False
    
    driver = webdriver.Firefox(options=options,
                               executable_path= f"{current_path}/{gecko_driver}", 
                               firefox_profile=firefox_profile)
    return driver

def get_url(page_url, driver):
    driver.get(page_url)
    sleep(page_load_time_out)
    close_popup = driver.find_elements_by_css_selector(".-close_popup")
    if len(close_popup) > 0:
        close_popup[0].click()
    return True

def get_products(driver):
    products = driver.find_elements_by_css_selector('section.products .sku')

    products_info = []

    for product in products:

        product_title = ''
        if len(product.find_elements_by_css_selector('h2.title span.name')) > 0:
            product_title = product.find_elements_by_css_selector('h2.title span.name')[0].text

        product_url = ''
        if len(product.find_elements_by_css_selector('a.link')) > 0:
            product_url = product.find_elements_by_css_selector('a.link')[0].get_attribute('href')
            product_name = product_url.replace(jumia_base_url+'/','')
            affiliate_url = f"https://c.jumia.io/?a=165688&c=10&p=r&E=kkYNyk2M4sk%3D&ckmrdr=https%3A%2F%2Fwww.jumia.com.eg%2Far%2F{product_name}&utm_campaign=165688"
            
        current_price = 0
        if len(product.find_elements_by_css_selector('span.price-box .price span')) > 0:
            current_price = product.find_elements_by_css_selector('span.price-box .price span')[0].get_attribute('data-price')
            if current_price != None:
                current_price = ceil( float(current_price) )


        old_price = 0
        if len(product.find_elements_by_css_selector('span.price-box .-old span')) > 0:
            old_price = product.find_elements_by_css_selector('span.price-box .-old span')[0].get_attribute('data-price')
            if old_price != None:
                old_price = ceil( float(old_price) )


        discount_percentage = 0
        discount_quantity = 0

        if current_price != 0 and current_price != None and old_price != 0 and old_price != None and current_price < old_price:
            discount_quantity = round( old_price - current_price )
            discount_percentage = round( 100 - ( (current_price / old_price) * 100 ) )

        
        if product_title == '' or product_url == '' or current_price == 0:
            continue
        
        product_info = {
            'product_title': product_title,
            'product_url': product_url,
            'affiliate_url': affiliate_url,
            'current_price': current_price,
            'old_price': old_price,
            'discount_percentage': discount_percentage,
            'discount_quantity': discount_quantity,
            'inserted_at': datetime.now(),
            'updated_at': datetime.now(),
            'published_at': False
        }
        
        if db.products.count_documents( { '$or': [ {'product_title': product_title}, {'product_url':product_url}, {'affiliate_url': affiliate_url} ]  } ) == 0:
            _ = db.products.insert_one( product_info )
        else:
            pd = db.products.find_one( { '$or': [ {'product_title': product_title}, {'product_url':product_url} ]  } )
            if pd['current_price'] != current_price or pd['old_price'] != old_price:
                # update prices
                db.products.update_one( {'_id': pd['_id'] },{'$set': 
                                                             {'current_price': current_price,
                                                             'old_price': old_price,
                                                             'discount_percentage': discount_percentage,
                                                             'discount_quantity':discount_quantity,
                                                              'affiliate_url': affiliate_url,
                                                             'updated_at': datetime.now(),
                                                             'published_at': False} }  )

        products_info.append( product_info )
    
    return products_info