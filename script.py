from multiprocessing import Queue, Process, Pool, Manager
import time
from datetime import datetime
import argparse
import logging
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import StaleElementReferenceException


SITE_NAME = ""


def timer(func):
    def wrapper(*args):
        start = time.time()
        func(*args)
        print(f"Время выполнения {func.__name__}: {time.time()-start}")
    return wrapper


def check_class(title:str):
    if os.path.exists(f"{title.capitalize()}.py"):
        return True
    else:
        return False


def run(que, checked):
    while True:
        url = check_url(que)
        logging.info(f"\t\tQUE: {list(que.queue)}")
        if not url:
            logging.info(f"\t\tBREAKBREAKBREAKBREAKBREAK")
            break
        else:
            checked.add(url)
            spider(url, que, checked)
    que.task_done()


def check_url(que):
    try:
        res = que.get(timeout=20)
    except Exception:
        res = False
    print(res)
    return res


def spider(link, que, checked):
    global SITE_NAME
    options = Options()
    options.add_argument('--headless')
    driver = webdriver.Chrome(os.path.abspath("./chromedriver"), chrome_options=options)
    driver.get(link)
    elements = driver.find_elements_by_xpath("//a")
    for element in elements:
        check_element(element, que, checked)
    logging.getLogger()
    logging.info(f"Проверяем {link}. Время: {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}")
    logging.info(f"\t\tCHECKED: {list(checked)}")
    que.task_done()
    driver.quit()


def check_element(element, que, checked):
    logging.getLogger()
    try:
        url = element.get_attribute('href')
        if url is not None and url not in que.queue and url.startswith(SITE_NAME) and url not in checked:
            que.put(url)
            logging.info(f"Такой url: {url} уже в списках. Время: {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}")
    except StaleElementReferenceException as e:
        logging.info(e, f"Время: {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}")


def create_py(pattern, title: str):
    logging.getLogger()
    with open(os.path.abspath(f"./Classes/{title.capitalize()}.py"), "w") as f:
        f.write(pattern)
    print(f"Класс {title.capitalize()} создан")
    logging.info(f"Класс {title.capitalize()} создан. Время: {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}")


def create_class(title:str):
    pattern = """
    # {0}
    class {1}:

        xpath_dict = dict()

        def __init__(self):
            pass"""
    logging.getLogger()
    pattern = pattern.format(datetime.now().strftime('%d-%m-%Y %H:%M:%S'), title)
    try:
        if not check_class(title):
            create_py(pattern, title)
    except FileExistsError:
        logging.info(
            f"Класс {title.capitalize()} уже создан. Время: {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}")
    except AttributeError:
        logging.info(
            f"Ошибка про создании класса. Время: {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}")


@timer
def main():
    que = Queue()
    checked = set()
    logging.basicConfig(filename="logs.log", level=logging.INFO)
    logging.info(f"\nНОВЫЙ ЗАПУСК. Время: {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}\n")
    try:
        os.makedirs(os.path.abspath("./Classes"))
    except FileExistsError:
        logging.info(f"Папка Classes уже создана. Время: {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}")
    parser = argparse.ArgumentParser(description="Spider-script")
    parser.add_argument('site', help='Сайт который надо обойти')
    args = parser.parse_args()
    global SITE_NAME
    try:
        SITE_NAME = args.site
        que.put(SITE_NAME)
        que.join()
    except Exception as e:
        print(e)


if __name__ == "__main__":
    main()
