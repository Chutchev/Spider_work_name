from bs4 import BeautifulSoup
from pprint import pprint
import requests
import time
import argparse
import DB
from sqlite3 import OperationalError
VERIFIED_URLS = {}
SITE = ''


def timer(func):
    def wrapper():
        start = time.time()
        func()
        print(f"Время выполнения {func.__name__}: {time.time()-start}")
    return wrapper


def read_html(url):
    try:
        response = requests.get(url=url)
        doc = response.content.decode('utf-8', errors='ignore')
        return str(doc)
    except ConnectionError:
        return "sgsg"


def find_urls(doc, filename, amount):
    urls = []
    VERIFIED_URLS[f"{SITE}{filename}"] = {'URLS': urls}
    if doc is not None:
        soup = BeautifulSoup(doc, features='html.parser')
        urls = soup.find_all('a')
        VERIFIED_URLS[f"{SITE}{filename}"] = {'URLS': urls}
        for url in urls:
            if url.get('href') not in VERIFIED_URLS.keys() and amount > 0:
                new_lines = read_html(f"{SITE}{url.get('href')}")
                find_urls(new_lines, url.get('href'), amount-1)
            else:
                break


@timer
def main():
    parser = argparse.ArgumentParser(description="Spider-script")
    parser.add_argument('site', help='Сайт который надо обойти')
    parser.add_argument('-amount', '-a', help='Количество переходов по ссылкам по всему сайту', required=False, default=1000)
    args = parser.parse_args()
    SITE = args.site
    amount = int(args.amount)
    doc = read_html(SITE)
    find_urls(doc, SITE, amount)
    pprint(VERIFIED_URLS)
    try:
        DB.create_db()
    except OperationalError:
        pass
    DB.insert_to_db(VERIFIED_URLS)


if __name__ == "__main__":
    main()
