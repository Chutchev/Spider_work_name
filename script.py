from bs4 import BeautifulSoup
import requests
import time
from datetime import datetime
import argparse
import requests.exceptions as re
import logging
import os
import threading
from queue import Queue, Empty


SITE_NAME = ""


def timer(func):
    def wrapper(*args):
        start = time.time()
        func(*args)
        print(f"Время выполнения {func.__name__}: {time.time()-start}")
    return wrapper


def create_right_url(url):
    if url is not None:
        if not url.startswith(SITE_NAME) and not url.startswith("http"):
            return f"{SITE_NAME}{url}"
        else:
            return url
    else:
        return None


def run(que, checked, errors):
    while True:
        url = check_url(que)
        logging.info(f"\t\tQUE: {list(que.queue)}, THREAD={threading.current_thread().name}")
        if not url:
            logging.info(f"\t\tBREAKBREAKBREAKBREAKBREAK")
            break
        else:
            if url not in errors:
                checked.put(url)
                spider(url, que, checked, errors)
    que.task_done()


def check_url(que):
    try:
        res = que.get(timeout=20)
    except Empty:
        res = False
    print(res, threading.current_thread().name)
    return res


def spider(url, que, checked, errors):
    global SITE_NAME
    response = read_html(url, errors)
    if response is not None:
        if response.status_code == 200:
            info = find_info(response.content.decode(encoding='utf-8', errors='ignore'), 'a')
            for link in info:
                if link is not None:
                    link = link.get('href')
                    link = create_right_url(link)
                    print("link -> ", link)
                    add_element_to_queue(link, que, checked, errors)
            logging.getLogger()
            print(url, threading.current_thread().name, threading.active_count(), len(checked.queue))
            logging.info(f"Проверяем {url}. Время: {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}")
            logging.info(f"\t\tCHECKED: {list(checked.queue)}, \tTHREAD: {threading.current_thread().name}")
        else:
            errors.add(url)
    que.task_done()


def add_element_to_queue(url, que, checked, errors):
    logging.getLogger()
    print(url, f"Thread name: {threading.current_thread().name}, active Threads: {threading.active_count()}")
    if url is not None and url not in que.queue and url.startswith(SITE_NAME) and url not in checked.queue and \
            url not in errors:
        que.put(url)
        logging.info(f"Добавлен url: {url}. Время: {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}")


def create_py(pattern, title: str):
    with open(os.path.abspath(f"./Classes/{title.capitalize()}.py"), "w") as f:
        f.write(pattern)
    logging.info(f"Класс {title.capitalize()} создан. Время: {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}")


def get_title(doc):
    title = find_info(doc, 'title')
    title = str(*title).replace("</title>", "").replace("<title>", "")
    return title


def read_html(url, errors):
    try:
        try:
            response = requests.get(url=url)
            if response.status_code == 200:
                print("\t\tREAD_HTML URL ->", url)
                return response
            else:
                errors.add(url)
                return None
        except (ConnectionError, re.ConnectionError):
            pass
    except (re.MissingSchema, re.InvalidSchema):
        return None


def find_info(doc, tag):
    soup = BeautifulSoup(doc, features='html.parser')
    info = soup.find_all(tag)
    return info


def create_class(doc, pattern):
    title = get_title(doc)
    try:
        create_py(pattern.format(title), title)
    except FileExistsError:
        logging.info(
            f"Класс {title.capitalize()} уже создан. Время: {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}")
    except AttributeError:
        logging.info(
            f"Ошибка про создании класса. Время: {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}")


def create_threads(func, *args):
    for _ in range(4):
        t = threading.Thread(target=func, args=args)
        t.daemon = True
        t.start()

@timer
def main():
    que = Queue()
    checked = Queue()
    errors = set()
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
        create_threads(run, que, checked, errors)
        que.join()
        print(len(checked.queue), len(errors))
        checked = set(checked.queue) - errors
        logging.info(f"\t\tCHEKED -> {checked} (Количество ссылок: {len(checked)}). Время: {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}")
    except Exception as e:
        print(e)


if __name__ == "__main__":
    main()