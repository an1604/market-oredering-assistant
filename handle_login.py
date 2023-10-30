# -*- coding: utf-8 -*-
"""
Created on Sat Oct 28 14:02:14 2023

@author: adina
"""
import requests
from requests.auth import HTTPBasicAuth
from bs4 import BeautifulSoup
from decouple import config

username = config('USERNAME')
passwd = config('PASSWORD')
# get the login page
login_page = config('LOGINPAGE')

from selenium import webdriver
from selenium.webdriver.common.by import By

driver = webdriver.Chrome()
driver.get(login_page)

# Getting the fields
usernameField = driver.find_element(By.ID ,'j_username' )
passwordField = driver.find_element(By.ID,'j_password' )
button = driver.find_element(By.CSS_SELECTOR, '.btn-login.btn-big')

# Sending keys
usernameField.send_keys(username)
passwordField.send_keys(passwd)
button.click()

print('Sccessfuly entered!')
driver.close()

