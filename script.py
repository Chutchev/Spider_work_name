import threading
from queue import Queue
import time
from datetime import datetime
import argparse
import logging
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import StaleElementReferenceException


SITE_NAME = ""


def thread(func):
    def wrapper(*args):
        if threading.active_count() < 4:
            threading.Thread(target=func, args=args).start()
    return wrapper


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
    options = Options()
    logging.basicConfig(filename="logs.log", level=logging.INFO)
    options.add_argument('--headless')
    driver = webdriver.Chrome(os.path.abspath("./chromedriver"), chrome_options=options)
    spider(que.queue[0], driver, que, checked)


@thread
def spider(link, driver, que, checked):
    global SITE_NAME
    logging.getLogger()
    print(link, threading.current_thread().name, threading.active_count())
    logging.info(f"Проверяем {link}. Время: {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}")
    if que.empty():
        que.task_done()
    que.get()
    driver.get(link)
    checked.put(link)
    create_class(driver.title)
    elements = driver.find_elements_by_xpath("//a")
    for element in elements:
        try:
            url = element.get_attribute('href')
            if url is not None and url not in que.queue and url.startswith(SITE_NAME) and url not in checked.queue:
                que.put(url)
        except StaleElementReferenceException as e:

            continue
    print(que.queue)
    que.task_done()
    try:
        spider(que.queue[0], driver, que, checked)
    except IndexError:
        print("УРААА")


def create_py(pattern, title: str):
    logging.getLogger()
    with open(os.path.abspath(f"./Classes/{title.capitalize()}.py"), "w") as f:
        f.write(pattern)
    print(f"Класс {title.capitalize()} создан")
    logging.info(f"Класс {title.capitalize()} создан. Время: {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}")


def create_class(title:str):
    pattern = """
    class {}:

        xpath_dict = dict()

        def __init__(self):
            pass"""
    logging.getLogger()
    pattern = pattern.format(title)
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
    checked = Queue()
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
        run(que, checked)
        que.join()
    except Exception as e:
        print(e)
    finally:
        print(checked.queue)


if __name__ == "__main__":
    main()
