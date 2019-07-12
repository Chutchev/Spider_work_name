from bs4 import BeautifulSoup
import requests
import time
from datetime import datetime
import argparse
import requests.exceptions as re
import logging
import os
from selenium import webdriver
from pprint import pprint
from selenium.common.exceptions import StaleElementReferenceException
driver = None
checked = []
site_name = ""
logging.basicConfig(filename="logs.log", level=logging.INFO)
pattern = ""


def timer(func):
    def wrapper(*args):
        start = time.time()
        func(*args)
        print(f"Время выполнения {func.__name__}: {time.time()-start}")
    return wrapper


def spider(ss):
    print(ss)
    driver.get(ss)
    elements = driver.find_elements_by_xpath("//a")
    for element in elements:
        try:
            url = element.get_attribute('href')
        except StaleElementReferenceException as e:
            continue
        if url not in checked:
            checked.append(url)
            try:
                create_class()
                spider(url)
            except StaleElementReferenceException:
                print(url)
    return checked


def create_py(title: str):
    global pattern
    with open(os.path.abspath(f"./Classes/{title.capitalize()}.py"), "w") as f:
        f.write(pattern)
    logging.info(f"Класс {title.capitalize()} создан. Время: {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}")


def create_class():
    global pattern
    title = driver.title
    pattern = pattern.format(title)
    try:
        create_py(title)
    except FileExistsError:
        logging.info(
            f"Класс {title.capitalize()} уже создан. Время: {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}")
    except AttributeError:
        logging.info(
            f"Ошибка про создании класса. Время: {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}")


@timer
def main():
    global driver
    driver = webdriver.Chrome(os.path.abspath("./chromedriver"))
    logging.info(f"НОВЫЙ ЗАПУСК. Время: {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}\n")
    try:
        os.makedirs(os.path.abspath("./Classes"))
    except FileExistsError:
        logging.info(f"Папка Classes уже создана. Время: {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}")
    parser = argparse.ArgumentParser(description="Spider-script")
    parser.add_argument('site', help='Сайт который надо обойти')
    args = parser.parse_args()
    global site_name
    global checked
    global pattern
    with open(os.path.abspath("./Шаблон.txt"), 'r') as f:
        pattern = f.read()
    site_name = args.site
    checked = spider(site_name)
    driver.quit()


if __name__ == "__main__":
    main()