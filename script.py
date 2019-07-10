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


def spider(ss):
    global checked
    global site_name
    response = read_html(ss)
    doc = response.content.decode('utf-8', errors='ignore')
    urls = [x.get('href') for x in find_info(doc, 'a') if x.get('href') not in checked]
    logging.info(f"Ссылка: {ss}. На сайте: {urls}. Время: {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}")
    while True:
        for url in urls:
            if url is not None:
                if not url.startswith(site_name) and not url.startswith("http"):
                    if url not in checked:
                        res = check_url(f"{site_name}{url}")
                        if res:
                            checked.append(url)
                            spider(f"{site_name}{url}")
                    else:
                        break
                else:
                    check_url(url)
                    checked.append(url)
        break


def create_py(title: str):
    pattern = f"""class {title.capitalize()}:
    
    def __init__(self):
        pass"""

    with open(os.path.abspath(f"./Classes/{title.capitalize()}.py"), "w") as f:
        f.write(pattern)

    logging.info(f"Класс {title.capitalize()} создан. Время: {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}")


def get_title(url):
    response = read_html(url)
    if response is not None:
        title = find_info(response.content.decode('utf-8', errors='ignore'), 'title')
        title = str(*title).replace("</title>", "").replace("<title>", "")
        try:
            create_py(title)
        except FileExistsError:
            logging.info(f"Класс {title.capitalize()} уже создан. Время: {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}")


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
    os.makedirs(os.path.abspath("./Classes"))
    parser = argparse.ArgumentParser(description="Spider-script")
    parser.add_argument('site', help='Сайт который надо обойти')
    args = parser.parse_args()
    global site_name
    site_name = args.site
    spider(site_name)
    for url in checked:
        get_title(url)


if __name__ == "__main__":
    main()