from bs4 import BeautifulSoup
import requests
import time
import argparse
import DB
import sqlite3
from pprint import pprint
import requests.exceptions as re
from sqlite3 import OperationalError
VERIFIED_URLS = {}
URLS = []


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


def return_url(doc):
    soup = BeautifulSoup(doc, features='html.parser')
    urls = soup.find_all('a')
    return urls


def find_urls(doc):
    soup = BeautifulSoup(doc, features='html.parser')
    urls = soup.find_all('a')
    return urls


def a_list(site, url, dicionary):
    if str(url).startswith('http'):
        response = read_html(url)
        if response.status_code == 200:
            doc = response.content.decode('utf-8', errors='ignore')
            dicionary[url] = find_urls(doc)
        else:
            print(response.status_code, url)
            dicionary[url] = []
    elif str(url).startswith('/'):
        response = read_html(f'{site}{url}')
        if response.status_code == 200:
            doc = response.content.decode('utf-8', errors='ignore')
            dicionary[f'{site}{url}'] = find_urls(doc)
        else:
            print(response.status_code, url)
            dicionary[f'{site}{url}'] = []
    else:
        response = read_html(f'{site}/{url}')
        if response.status_code == 200:
            doc = response.content.decode('utf-8', errors='ignore')
            dicionary[f'{site}/{url}'] = find_urls(doc)
        else:
            print(response.status_code, url)
            dicionary[f'{site}/{url}'] = []
    return dicionary


def fill_base_dict(urls, site):
    for url in urls:
        url = url.get('href')
        if url not in VERIFIED_URLS.keys():
            print(f"{url}")
            dictionary = a_list(site, url, VERIFIED_URLS)
            try:
                VERIFIED_URLS[url] = dictionary.values()
            except AttributeError:
                VERIFIED_URLS[url] = []


def fill_extra_dict(site):
    extra_dict = {}
    for value in VERIFIED_URLS.values():
        for url in value:
            try:
                url = url.get('href')
                if url not in VERIFIED_URLS.keys():
                    print(f'fill_extra_dict: {url}')
                    dictionary = a_list(site, url, extra_dict)
                    try:
                        extra_dict[url] = dictionary.values()
                    except AttributeError:
                        pass
            except AttributeError:
                pass
    return extra_dict


def select_all_into_db(table_name):
    with sqlite3.connect("URLS.db") as conn:
        cur = conn.cursor()
        data = cur.execute(f"SELECT * FROM {table_name}")
        strokes = data.fetchall()
    return strokes


@timer
def main():
    parser = argparse.ArgumentParser(description="Spider-script")
    parser.add_argument('site', help='Сайт который надо обойти')
    args = parser.parse_args()
    site_name = args.site
    table_name = site_name.split("/")[2].split('.')
    print(table_name)
    site = "http://" + '.'.join(table_name)
    print(site)
    table_name = "_".join(table_name)
    response = read_html(site_name)
    full_dict = {}
    if response.status_code == '404':
        VERIFIED_URLS[site_name] = []
    else:
        doc = response.content.decode('utf-8', errors='ignore')
        urls = find_urls(doc)
        fill_base_dict(urls, site)
        extra_dict = fill_extra_dict(site)
        full_dict = {**VERIFIED_URLS, **extra_dict}
    dont = {}
    for k, v in full_dict.items():
        if len(v) == 0:
            dont[k] = [].append(v)
    pprint(dont)
    try:
        DB.create_db(table_name)
    except OperationalError:
        pass
    DB.update_db(dont.values(), table_name)
    strokes = select_all_into_db(table_name)
    pprint(strokes)

if __name__ == "__main__":
    main()
