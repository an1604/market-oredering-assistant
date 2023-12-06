# -*- coding: utf-8 -*-
"""
Created on Mon Oct 30 09:41:14 2023

@author: adina
"""
from dotenv import load_dotenv
import os
import pymysql
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time
from decouple import config
import re
from selenium.common.exceptions import NoSuchElementException

dotenv_path = os.path.join(os.path.dirname(__file__), '..', '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)
else:
    print("Warning: .env file not found.")

# Connect to the MySQL database
conn = pymysql.connect(
    host=os.environ.get('DB_HOST'),
    user=os.environ.get('DB_USER'),
    password=os.environ.get('DB_PASSWORD'),
    db=os.environ.get('DB_NAME')
)
cur = conn.cursor()
cur.execute('USE scraping')


# Function to insert a product into the database


def insert_to_DB(name, price, img, buy_button, description, category):
    try:
        cur.execute(
            "INSERT INTO products (name, price, image, buy_button, description, category) VALUES (%s, %s, %s, %s, %s, %s)",
            (name, price, img, buy_button, description, category)
        )
        conn.commit()
        print(f"Product: {name}, Price: {price}, Image: {img}, Category: {category} inserted into the DB!")
        return True
    except Exception as e:
        print(f"Error inserting into the DB: {str(e)}")
        return False



# Function to scroll to the bottom of the page
def scroll_to_bottom(driver):
    last_height = 0
    while True:
        current_height = driver.execute_script(
            "return document.body.scrollHeight")
        if current_height == last_height:
            break
        driver.execute_script(
            "window.scrollTo(0, document.body.scrollHeight);")
        last_height = current_height
        time.sleep(2)

def get_category_name(driver):
    try:
        category = driver.find_element(By.CLASS_NAME, 'titleSection').text
    except NoSuchElementException:
        category = 'promotion'
    return category


def get_page(product_element):
    try:
        bs = BeautifulSoup(product_element.get_attribute(
            "outerHTML"), 'html.parser')
        return bs
    except NoSuchElementException as e:
        print("Error: Element not found on the page. Skipping this page.")
        return None

# TODO: add a description for all the insert_product functions!
"""------------------------------------------------------------------"""
def insert_product_by_unit(bs, category, buy_button):
    name_temp = bs.find('span', {'data-target': '#productModal'})
    name = name_temp.text if name_temp else 'no name for this one'
    filtered_price = re.findall(
        r'\d+\.\d+', bs.find('span', {'class': 'number'}).text)
    if filtered_price:
        price = float(filtered_price[0])
    else:
        price = 0.0
    img = bs.find('img', {'class': 'pic'})['src']
    if insert_to_DB(name, price, img, buy_button, category):
        print(
            f'Product: {name} , Price : {price} inserted into the DB!')


def insert_product_by_package(bs, buy_button, category):
    name_temp = bs.find('span', {'data-target': '#productModal'})
    name = name_temp.text if name_temp else 'no name for this one'
    filtered_price = re.findall(
        r'\d+\.\d+', bs.find('span', {'itemprop': 'price'}).text)
    if filtered_price:
        price = float(filtered_price[0])
    else:
        price = 0.0
    img = bs.find('img', {'class': 'pic'})['src']
    if insert_to_DB(name, price, img, buy_button, category):
        print(f'Product: {name}, Price: {price} inserted into the DB!')


def insert_product_by_weight(bs, buy_button, category):
    name_temp = bs.find('span', {'data-target': '#productModal'})
    name = name_temp.text if name_temp else 'no name for this one'
    filtered_price = re.findall(
        r'\d+\.\d+', bs.find('span', {'class': 'number'}).text)
    if filtered_price:
        price = float(filtered_price[0])
    else:
        price = 0.0
    img = bs.find('img', {'class': 'pic'})['src']
    if insert_to_DB(name, price, img, buy_button, category):
        print(f'Product: {name}, Price: {price} inserted into the DB!')

"""------------------------------------------------------------------"""

def add_promotion_to_DB(bs, buy_button, category):
    description_tmp = bs.find('span', {'class': 'description'})
    price_tmp = bs.find('span', {'class': 'priceTxt'})
    try:
        price = float(price_tmp.text) if price_tmp and price_tmp.text else 0.0
    except ValueError as ve:
        price = 0.0
        print(f"Error converting price to float: {ve}")

    description = description_tmp.text if description_tmp else 'This element has no description'
    img_element = bs.find('img', {'class': 'pic'})
    img = img_element.text if img_element else 'no image found'

    if description is not None and price is not None:
        try:
            if insert_to_DB(name='promotion', price=price, category=category, buy_button=buy_button,
                            img=img, description=description):
                print('Promotion: {} inserted into the DB!'.format(description))
        except Exception as e:
            error_message = str(e)
            print('An exception occurred when trying to insert promotions to the DB:', error_message)
    else:
        print('Variable is None: Either description or price is None.')



def get_buy_button(bs):
    return bs.find('button', {'class': 'btn js-add-to-cart js-enable-btn miglog-btn-add'}).text \
        if bs.find('button', {'class': 'btn js-add-to-cart js-enable-btn miglog-btn-add'}) is not None \
        else None


def get_products_from_page(url):
    driver = webdriver.Chrome()
    driver.get(url)

    # Handle the ad (if present)
    try:
        ad_btn = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'dy-lb-close')))
        ad_btn.click()
    except Exception as e:
        print(f"An error occurred while waiting for the ad: {str(e)}")

    # Wait for some time to ensure the page is fully loaded
    time.sleep(5)

    scroll_to_bottom(driver)

    # Find all product elements and scrape
    category = get_category_name(driver)

    product_elements = driver.find_elements(By.TAG_NAME, 'li')
    for product_element in product_elements:
        bs = get_page(product_element)  # Pass individual element here

        if bs is not None:
            buy_button = get_buy_button(bs)

            # getting product that is calculated by unit
            if 'miglog-prod miglog-sellingmethod-by_unit' in product_element.get_attribute('class'):
                insert_product_by_unit(bs, category, buy_button)

            # getting product that is calculated by package
            elif 'miglog-prod miglog-sellingmethod-by_package' in product_element.get_attribute('class'):
                insert_product_by_package(bs, buy_button, category)

            # getting product that is calculated by weight
            elif 'miglog-prod miglog-sellingmethod-by_weight' in product_element.get_attribute('class'):
                insert_product_by_weight(bs, buy_button, category)

            # checking promotions
            else:
                promotion = bs.find('div', {
                    'class': 'tile miglog-promo no-draggable miglog-promo-single miglog-sellingmethod-by_unit {{cssHasCharcteristics}} has-characteristics'
                })
                if promotion:
                    add_promotion_to_DB(bs, buy_button, category)

    driver.quit()


# Main script
if __name__ == "__main__":
    # Create a new instance of the Chrome driver
    driver = webdriver.Chrome()

    # Navigate to the web page
    url = config('HOMEPAGE')
    driver.get(url)

    # Handle the ad (if present)
    try:
        ad_btn = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'dy-lb-close')))
        ad_btn.click()
    except Exception as e:
        print(f"An error occurred while waiting for the ad: {str(e)}")

    # Wait for some time to ensure the page is fully loaded
    time.sleep(5)

    # Find all links to product pages
    listItems = driver.find_element(By.ID, 'secondMenu2')
    all_links = listItems.find_elements(By.TAG_NAME, 'a')
    products_links = [link.get_attribute("href") for link in all_links]

    # Process each page and scrape products
    for link in products_links:
        get_products_from_page(link)

    # do the same for the pages that need more preprocessing
    meat_url = 'https://www.shufersal.co.il/online/he/A07'
    driver = webdriver.Chrome()
    driver.get(meat_url)

    # Wait for the element to be present
    wait = WebDriverWait(driver, 10)
    ul_element = wait.until(EC.presence_of_element_located(
        (By.CLASS_NAME, 'categoryBannerComponent')))

    html_source = driver.page_source

    bs = BeautifulSoup(html_source, 'html.parser')

    ul = bs.find('section', {'class': 'categoryBannerComponent'})
    ul_html = ul.prettify()

    # Create a BeautifulSoup object from the HTML content of the `ul` element
    ul_soup = BeautifulSoup(ul_html, 'html.parser')

    links = ul_soup.find_all('a')
    link_list = []
    for link in links:
        href = link.get('href')
        link_list.append(href)

    for link in link_list:
        get_products_from_page(link)

    driver.quit()
    conn.close()