import json
import random
import time
from urllib.parse import unquote

import requests as requests
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup

headers = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36',
    'accept': '*/*'
}

def get_source_html(url):
    driver = webdriver.Chrome()
    driver.maximize_window()
    try:
        driver.get(url)
        driver.implicitly_wait(3)

        while True:

            if driver.find_elements(By.CLASS_NAME, 'hasmore-text'):
                with open('source_page.html', 'w', encoding="utf-8") as file:
                    file.write(driver.page_source)
                break
            else:
                find_more_element = driver.find_element(By.CLASS_NAME, 'catalog-button-showMore')
                actions = ActionChains(driver)
                actions.move_to_element(find_more_element).perform()
                driver.implicitly_wait(90)

    except Exception as _ex:
        print(_ex)
    finally:
        driver.quit()

def get_items_urls(file_path):
    with open(file_path, encoding='utf-8') as file:
        src = file.read()

    soup = BeautifulSoup(src, 'lxml')
    items_divs = soup.find_all('div', class_='minicard-item__info')
    urls = []
    for item in items_divs:
        item_url = item.find('h2', class_='minicard-item__title').find('a').get('href')
        urls.append(item_url)

    with open('urls.txt', 'w', encoding='utf-8') as file:
        for url in urls:
            file.write(f'{url}\n')

def get_data(file_path):
    with open(file_path, encoding='utf-8') as file:
        urls_list = [url.strip() for url in file.readlines()]

    result_list = []
    for url in urls_list:
        response = requests.get(url=url, headers=headers)
        soup = BeautifulSoup(response.text, 'lxml')

        try:
            item_name = soup.find('span', {'itemprop': "name"}).text.strip()
        except:
            item_name = None

        item_phones_list = []
        try:
            item_phones = soup.find("div", class_="service-phones-list").find_all("a", class_="js-phone-number")

            for phone in item_phones:
                item_phone = phone.get("href").split(":")[-1].strip()
                item_phones_list.append(item_phone)
        except:
            item_phones_list = None

        try:
            item_address = soup.find('address', class_='iblock').text.strip()
        except:
            item_address = None

        try:
            item_site = soup.find('div', class_='service-website-value').find('a').get('href')
        except:
            item_site = None

        social_networks_list = []
        try:
            item_social_networks = soup.find('div', class_='js-service-socials').find_all('a')
            for item in item_social_networks:
                sn_url = item.get('href')
                sn_url = unquote(sn_url.split("?to=")[-1]).split("&")[0]
                social_networks_list.append(sn_url)
        except:
            social_networks_list = None

        result_list.append(
            {
                "name": item_name,
                "url": url,
                "phones": item_phones_list,
                "address": item_address,
                "site": item_site,
                "social_networks": social_networks_list
            }
        )

        time.sleep(random.randrange(2,5))

    with open('result.json', 'w', encoding='utf-8') as file:
        json.dump(result_list, file, indent=4, ensure_ascii=False)

def main():
    get_source_html(url='https://spb.zoon.ru/medical/?search_query_form=1&m%5B5200e522a0f302f066000055%5D=1&center%5B%5D=59.91878264665887&center%5B%5D=30.342586983263384&zoom=10')
    get_items_urls(file_path='file_path')
    get_data(file_path='file_path')

if __name__ == '__main__':
    main()