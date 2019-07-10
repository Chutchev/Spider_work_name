from bs4 import BeautifulSoup
import requests
import time
from datetime import datetime
import argparse
import requests.exceptions as re
import logging
import os


checked = []
site_name = ""
logging.basicConfig(filename="logs.log", level=logging.INFO)
pattern = ""


def create_right_url(url):
    if url is not None:
        if not url.startswith(site_name) and not url.startswith("http"):
            return f"{site_name}{url}"
        else:
            return url
    else:
        return None


def spider(ss):
    global checked
    global site_name
    response = read_html(ss)
    print(ss, response)
    doc = response.content.decode('utf-8', errors='ignore')
    urls = [create_right_url(x.get('href')) for x in find_info(doc, 'a') if create_right_url(x.get('href')) is not None and create_right_url(x.get('href')) not in checked]
    logging.info(f"Ссылка: {ss}. На сайте: {urls}. Время: {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}")
    while True:
        for url in urls:
            if url is not None:
                if url.startswith(site_name):
                    if url not in checked:
                        res = check_url(url)
                        if res:
                            checked.append(url)
                            create_class(url, pattern)
                            spider(url)
                    else:
                        break
                else:
                    check_url(url)
                    checked.append(url)
        break


def create_py(pattern, title: str):
    with open(os.path.abspath(f"./Classes/{title.capitalize()}.py"), "w") as f:
        f.write(pattern)
    logging.info(f"Класс {title.capitalize()} создан. Время: {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}")


def get_title(url):
    if not url.startswith(site_name) and not url.startswith("http"):
        response = read_html(f"{site_name}{url}")
    else:
        response = read_html(url)
    if response is not None:
        title = find_info(response.content.decode('utf-8', errors='ignore'), 'title')
        title = str(*title).replace("</title>", "").replace("<title>", "")
        return title


def timer(func):
    def wrapper():
        start = time.time()
        func()
        print(f"Время выполнения {func.__name__}: {time.time()-start}")
    return wrapper


def read_html(url):
    try:
        try:
            response = requests.get(url=url)
            return response
        except (ConnectionError, re.ConnectionError):
            pass
    except (re.MissingSchema, re.InvalidSchema):
        return None


def find_info(doc, tag):
    soup = BeautifulSoup(doc, features='html.parser')
    info = soup.find_all(tag)
    return info


def create_class(url, pattern):
    title = get_title(url)
    try:
        create_py(pattern.format(title), title)
    except FileExistsError:
        logging.info(
            f"Класс {title.capitalize()} уже создан. Время: {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}")
    except AttributeError:
        logging.info(
            f"Ошибка про создании класса. Время: {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}")


def check_url(url):
    try:
        response = requests.get(url)
        if 199 < response.status_code < 400 and response is not None:
            print(url, response.status_code)
            return True
        else:
            print(url, response.status_code)
            return False
    except (re.ConnectionError, re.MissingSchema) as e:
        print(url, e)
        return False

@timer
def main():
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
    spider(site_name)
    checked = set(checked)


if __name__ == "__main__":
    main()