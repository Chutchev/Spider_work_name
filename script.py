from bs4 import BeautifulSoup
import requests
import time
import argparse
import DB
import requests.exceptions as re
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
        try:
            response = requests.get(url=url)
            doc = response.content.decode('utf-8', errors='ignore')
            return str(doc)
        except (ConnectionError, re.ConnectionError):
            doc = None
            return doc
    except (re.MissingSchema, re.InvalidSchema):
        return "Invalid URL"


def find_urls(doc, filename, amount):
    urls = []
    VERIFIED_URLS[f"{SITE}{filename}"] = {'URLS': urls}
    if doc is not None:
        soup = BeautifulSoup(doc, features='html.parser')
        urls = soup.find_all('a')
        VERIFIED_URLS[f"{SITE}{filename}"] = urls
        for url in urls:
            if url.get('href') not in VERIFIED_URLS.keys() and amount > 0:
                print(f"Осталось ссылок: {amount}")
                amount -= 1
                if str(url.get('href')).startswith("http"):
                    new_lines = read_html(f"{url.get('href')}")
                    find_urls(new_lines, url.get('href'), amount)
                else:
                    new_lines = read_html(f"{SITE}/{url.get('href')}")
                    find_urls(new_lines, url.get('href'), amount)
            else:
                break
    else:
        VERIFIED_URLS[f"{SITE}{filename}"] = "Не найдено"

@timer
def main():
    parser = argparse.ArgumentParser(description="Spider-script")
    parser.add_argument('site', help='Сайт который надо обойти')
    parser.add_argument('-amount', '-a', help='Количество переходов по ссылкам по всему сайту', required=False,
                        default=1000)
    args = parser.parse_args()
    SITE = args.site
    amount = int(args.amount)
    doc = read_html(SITE)
    find_urls(doc, SITE, amount)
    table_name = SITE.split("/")[2].split('.')
    table_name = "_".join(table_name)
    dont_working = [k for k, v in VERIFIED_URLS.items() if len(v) == 0 and k != 'None']
    try:
        DB.create_db(table_name)
    except OperationalError:
        pass
    DB.update_db(dont_working, table_name)


if __name__ == "__main__":
    main()
