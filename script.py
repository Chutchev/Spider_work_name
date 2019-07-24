import threading
from threading import Lock
from queue import Queue
from queue import Empty
import time
from datetime import datetime
import argparse
import logging
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import StaleElementReferenceException, NoSuchElementException


SITE_NAME = ""
lock = Lock()


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
        url = que.get(timeout=20)
        logging.info(f"\t\tQUE: {list(que.queue)}, THREAD={threading.current_thread().name}")
        if not url:
            logging.info(f"\t\tBREAKBREAKBREAKBREAKBREAK")
            break
        else:
            checked.add(url)
            spider(url, que, checked)
    que.task_done()


def fill_xpath_dict(driver, els):
    print('fill')
    checked = set()
    a = {'a': 'ссылку',
         'h1': 'текст',
         'input': 'кнопку',
         'ul': 'список',
         'li': 'пункт',
         'span': 'блок',
         'div': 'блок',
         'label': 'текст',
         'button': 'кнопку'
         }
    tags = {'a': ['href', 'text'],
            'h1': ['text', 'id'],
            'input': ['id', 'type'],
            'ul': ['role', 'class'],
            'li': ['class'],
            'span': ['class'],
            'div': ['class', 'id'],
            'label': ['text', 'id'],
            'button': ['id', 'class']
            }
    for tag, attributes in tags.items():
        if a[tag] not in els.keys():
            els[a[tag]] = []
        elements = driver.find_elements_by_tag_name(tag)
        for element in elements:
            xpathes = {}
            if element.text in checked:
                continue
            checked.add(element.text)
            for attribute in attributes:
                value = element.get_attribute(attribute)
                xpathes[element.text] = ''
                if attribute == 'text':
                    xpathes[element.text] = (f"//{tag}[{attribute}()='{value}']")
                else:
                    xpathes[element.text] = (f"//{tag}[@{attribute}='{value}']")
            try:
                if driver.find_elements_by_xpath(xpathes[element.text]):
                    els[a[tag]].append(xpathes)
            except Exception:
                print(xpathes, element.text)
    return els, checked


def check_elem(xpath, driver):
    print(xpath)
    try:
        return driver.find_element_by_xpath(xpath)
    except NoSuchElementException:
        return False


def spider(link, que, checked):
    global lock
    global SITE_NAME
    options = Options()
    options.add_argument('--headless')
    driver = webdriver.Chrome(os.path.abspath("./chromedriver"), chrome_options=options)
    driver.get(link)
    elements = driver.find_elements_by_xpath("//a")
    for element in elements:
        check_element(element, que, checked)
    els = {}
    thread = threading.Thread(target=create_class, args=(driver, els))
    thread.start()
    thread.join()
    print(link, threading.current_thread().name, threading.active_count(), len(checked))
    logging.info(f"Проверяем {link}. Время: {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}")
    logging.info(f"\t\tCHECKED: {list(checked)}, \tTHREAD: {threading.current_thread().name}")
    que.task_done()
    driver.quit()


def check_element(element, que, checked):
    logging.getLogger()
    try:
        url = element.get_attribute('href')
        print(url, f"Thread name: {threading.current_thread().name}, active Threads: {threading.active_count()}")
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


def create_class(driver, xpath_dict):
    title = driver.title
    pattern = """
    # {0}
    
    class {1}:

        xpath_dict = {2}

        def __init__(self):
            pass"""
    fill_xpath_dict(driver, xpath_dict)
    logging.getLogger()
    pattern = pattern.format(datetime.now().strftime('%d-%m-%Y %H:%M:%S'), title, xpath_dict)
    try:
        if not check_class(title):
            create_py(pattern, title)
    except FileExistsError:
        logging.info(
            f"Класс {title.capitalize()} уже создан. Время: {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}")
    except AttributeError:
        logging.info(
            f"Ошибка про создании класса. Время: {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}")


def create_threads(que, checked):
    for _ in range(4):
        t = threading.Thread(target=run, args=(que, checked))
        t.daemon = True
        t.start()


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
        create_threads(que, checked)
        que.join()
    except Exception as e:
        print(e)


if __name__ == "__main__":
    main()
