import requests
from bs4 import BeautifulSoup
from requests.exceptions import HTTPError, RequestException
import pandas as pd

class Product:
    def __init__(self, name, price, img):
        self.name = name
        self.price = price
        self.img = img

class Crawler:
    def getPage(self, url):
        try:
            req = requests.get(url)
            req.raise_for_status()  # Raise an HTTPError if the request is not successful
        except HTTPError as e:
            print('HTTP error: {}'.format(e))
            return None
        except RequestException as e:
            print('RequestException: {}'.format(e))
            return None
        return BeautifulSoup(req.text, 'html.parser')
    
    def crawl_category(self, url):
        bs = self.getPage(url)
        if bs is None:
            return None  # Handle the case where the page cannot be retrieved

        category_name = bs.find('h1', {'class': 'titleSection'})
        if category_name is not None:
            category_name = category_name.text
              

            products = bs.find_all('li', {'class': 'miglog-prod miglog-sellingmethod-by_unit'})
            products_list = []
            for product in products:
                name = product.find('span', {'data-target': '#productModal'})
                if name is not None:
                    name = name.text
                else:
                    name = "Unknown Name"  # Provide a default value or handle the error gracefully
                price = product.find('span', {'class': 'number'})
                if price is not None:
                    price = price.text
                else:
                    price = "Unknown Price"  # Provide a default value or handle the error gracefully
                img = product.find('img', {'class': 'pic'})
                if img is not None:
                    img = img['src']
                else:
                    img = "Unknown Image URL"  # Provide a default value or handle the error gracefully
                products_list.append(Product(name, price, img))
            data = pd.DataFrame()
            
            data['Name'] = [product.name for product in products_list]
            data['Price'] = [product.price for product in products_list]
            data['Image'] = [str(product.img) for product in products_list]
            return {'Category': category_name, 'Data': data}
            
            
    
    def crawl(self, url):
        bs = self.getPage(url)
        if bs is None:
            return None  # Handle the case where the page cannot be retrieved

        links = bs.find('div', {'id': 'headerBottom2'}).find('ul', {'id': 'secondMenu2'}).find_all('li', {'data=category': 'A040801'})
        
        all_links = []
        for link in links:
            link_to_category = link.find('ul')
            all_links.append(link_to_category)
        categories = []
        for link in all_links:
            url = 'https://www.shufersal.co.il' + link
            category = self.crawl_category(url)
            if category is not None:
                categories.append(category)
        return categories

url = 'https://www.shufersal.co.il/online/he/A'
crawler = Crawler()
all_categories = crawler.crawl(url)



