# -*- coding: utf-8 -*-
"""
Created on Mon Oct 30 09:41:14 2023

@author: adina
"""
import pymysql
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time 
from decouple import config

DB_HOST = config('DB_HOST')
DB_USER = config('DB_USER')
DB_PASSWORD = config('DB_PASSWORD')
DB_NAME = config('DB_NAME')


# Connect to the MySQL database
conn = pymysql.connect(
    host=DB_HOST,
    user=DB_USER,
    password=DB_PASSWORD,
    db=DB_NAME
)
cur = conn.cursor()
cur.execute('USE scraping')

# Function to insert a product into the database
def insert_to_DB(name, price, img):
    try:
        cur.execute("INSERT INTO products (name, price, image) VALUES (%s, %s, %s)", (name, price, img))
        conn.commit()
        return True
    except Exception as e:
        print(f"Error inserting into the DB: {str(e)}")
        return False

# Function to scroll to the bottom of the page
def scroll_to_bottom(driver):
    last_height = 0
    while True:
        current_height = driver.execute_script("return document.body.scrollHeight")
        if current_height == last_height:
            break
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        last_height = current_height
        time.sleep(2)

# Function to scrape and insert products from a page
def get_products_from_page(url):
    driver = webdriver.Chrome()
    driver.get(url)

    # Handle the ad (if present)
    try:
        ad_btn = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'dy-lb-close')))
        ad_btn.click()
    except Exception as e:
        print(f"An error occurred while waiting for the ad: {str(e)}")

    # Wait for some time to ensure the page is fully loaded
    time.sleep(5)

    scroll_to_bottom(driver)

    # Find all product elements and scrape
    product_elements = driver.find_elements(By.TAG_NAME, 'li')

    for product_element in product_elements:
        if 'miglog-prod miglog-sellingmethod-by_unit' in product_element.get_attribute('class'):
            bs = BeautifulSoup(product_element.get_attribute("outerHTML"), 'html.parser')
            name = bs.find('span', {'data-target': '#productModal'}).text
            price = float(bs.find('span', {'class': 'number'}).text)
            img = bs.find('img', {'class': 'pic'})['src']
            if insert_to_DB(name, price, img):
                print(f'Product: {name} inserted into the DB!')

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
        ad_btn = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'dy-lb-close')))
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

    # Close the browser
    driver.quit()

    # Close the database connection
    conn.close()








