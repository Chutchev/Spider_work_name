from multiprocessing import Process, current_process
from AdditionalClasses.my_queue import NewQueue
from AdditionalClasses.my_manager import NewManager
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
    print("run")
    logging.getLogger()
    while True:
        print('TRUE', current_process().name)
        try:
            url = check_url(que)
            logging.info(f"\t\tQUE: {que.get_attribute('queue')}")
            if not url:
                print('not url')
                logging.info(f"\t\tBREAKBREAKBREAKBREAKBREAK")
                break
            else:
                print('spider, ', url)
                checked.append(url)
                spider(url, que, checked)
        except IndexError:
            break


def check_url(que):
    try:
        res = que.get(timeout=20)
    except Exception:
        res = False
    print(res)
    return res


def spider(link, que, checked):
    global SITE_NAME
    print("LINK -> ", link, " proccess -> ", current_process().name)
    options = Options()
    options.add_argument('--headless')
    driver = webdriver.Chrome(os.path.abspath("./chromedriver"), chrome_options=options)
    driver.get(link)
    elements = driver.find_elements_by_xpath("//a")
    for element in elements:
        check_element(element, que, checked)
    logging.getLogger()
    logging.info(f"Проверяем {link}. Время: {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}")
    logging.info(f"\t\tCHECKED: {checked}")
    driver.quit()
    que.task_done()


def check_element(element, que, checked):
    logging.getLogger()
    try:
        url = element.get_attribute('href')
        print(url, current_process().name)
        if url is not None and url not in que.get_attribute('queue') and url.startswith(SITE_NAME) and url not in checked:
            que.put(url)
        else:
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


def create_proccess(func, *args):
    for _ in range(4):
        proc = Process(target=func, args=args)
        proc.start()
    proc.join()


@timer
def main():
    NewManager().register("Queue", NewQueue)
    manager = NewManager()
    manager.start()
    que = manager.Queue()
    checked = manager.list()
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
        create_proccess(run, que, checked)
        que.join()
    except Exception as e:
        print(e)


if __name__ == "__main__":
    main()
