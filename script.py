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


def spider(ss):
    global checked
    global site_name
    checked = list(set(checked))
    response = read_html(ss)
    print(ss, ss in checked)
    doc = response.content.decode('utf-8', errors='ignore')
    create_class(doc, pattern)
    urls = [create_right_url(x.get('href')) for x in find_info(doc, 'a') if create_right_url(x.get('href')) is not None
            and create_right_url(x.get('href')) not in checked]
    logging.info(f"Ссылка: {ss}. На сайте: {urls}. Время: {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}")
    for url in urls:
            if url.startswith(site_name):
                if url not in checked:
                    checked.append(url)
                    spider(url)
                else:
                    break


def create_py(pattern, title: str):
    with open(os.path.abspath(f"./Classes/{title.capitalize()}.py"), "w") as f:
        f.write(pattern)
    logging.info(f"Класс {title.capitalize()} создан. Время: {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}")


def get_title(doc):
    title = find_info(doc, 'title')
    title = str(*title).replace("</title>", "").replace("<title>", "")
    return title


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


if __name__ == "__main__":
    main()