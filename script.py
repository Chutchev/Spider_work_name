import time
from datetime import datetime
import argparse
import logging
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
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


def create_right_url(url):
    if url is not None:
        if not url.startswith(site_name) and not url.startswith("http"):
            return f"{site_name}{url}"
        else:
            return url
    else:
        return None


def check_class(title:str):
    if os.path.exists(f"{title.capitalize()}.py"):
        return True
    else:
        return False


def spider(ss):
    global checked
    global site_name
    driver.get(ss)
    elements = driver.find_elements_by_xpath("//a")
    for element in elements:
        try:
            url = element.get_attribute('href')

        except StaleElementReferenceException as e:
            continue
        if url not in checked and url is not None and url.startswith(site_name):
            print(url)
            checked.append(url)
            title = driver.title
            if check_class(title):
                create_class(title)
            spider(url)
    return checked


def create_py(title: str):
    global pattern
    with open(os.path.abspath(f"./Classes/{title.capitalize()}.py"), "w") as f:
        f.write(pattern)
    print(f"Класс {title.capitalize()} создан")
    logging.info(f"Класс {title.capitalize()} создан. Время: {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}")


def create_class(title:str):
    global pattern
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
    options = Options()
    options.add_argument('--headless')
    driver = webdriver.Chrome(os.path.abspath("./chromedriver"), chrome_options=options)
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
    try:
        site_name = args.site
        checked = spider(site_name)
    except Exception as e:
        print(e)
    finally:
        driver.quit()


if __name__ == "__main__":
    main()