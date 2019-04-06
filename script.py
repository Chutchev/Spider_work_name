from bs4 import BeautifulSoup
import requests
import time
import argparse
import DB
import sqlite3
from pprint import pprint
import requests.exceptions as re
from sqlite3 import OperationalError
import logging


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


def find_urls(doc):
    soup = BeautifulSoup(doc, features='html.parser')
    urls = soup.find_all('a')
    return urls


def check_url(url):
    try:
        response = requests.get(url)
        if 199 < response.status_code < 400 and response is not None:
            return True
        else:
            print(url, response.status_code)
            return False
    except re.ConnectionError as e:
        print(url, e)
        return False


def fill_base_list(urls, url_list: list):
    for url in urls:
        url = url.get('href')
        if url not in url_list:
            url_list.append(url)
    return url_list


def fill_breaking_url_list(urls, site):
    breaking = []
    for url in urls:
        if str(url).startswith('http'):
            if not check_url(url):
                breaking.append(url)
        elif str(url).startswith('/'):
            if not check_url(f'{site}{url}'):
                breaking.append(f'{site}{url}')
        else:
            if not check_url(f'{site}/{url}'):
                breaking.append(f'{site}/{url}')
    return breaking


def select_all_into_db(table_name):
    with sqlite3.connect("URLS.db") as conn:
        cur = conn.cursor()
        data = cur.execute(f"SELECT * FROM {table_name}")
        strokes = data.fetchall()
    return strokes


def func(base_list, site):
    print('func')
    for url in base_list:
        print(url)
        if str(url).startswith(site):
            doc = read_html(url)
            logging.error("{url} startswith")
            if doc is not None:
                doc = doc.content.decode('utf-8', errors='ignore')
                urls = find_urls(doc)
                a_list = fill_base_list(urls, base_list)
                for extra_url in a_list:
                    if extra_url not in base_list:
                        print(extra_url)
                        base_list.append(extra_url)
        else:
            logging.error(f"ERROR: {url} in base_list")
    return base_list

@timer
def main():
    logging.basicConfig(filename="log.log")
    parser = argparse.ArgumentParser(description="Spider-script")
    parser.add_argument('site', help='Сайт который надо обойти')
    args = parser.parse_args()
    site_name = args.site
    table_name = site_name.split("/")[2].split('.')
    site = "http://" + '.'.join(table_name)
    table_name = "_".join(table_name).replace("-", '__')
    response = read_html(site_name)
    doc = response.content.decode('utf-8', errors='ignore')
    urls = find_urls(doc)
    new_list = fill_base_list(urls, [])
    base_list = [site_name, *new_list]
    old = []
    while old != base_list:
        old = base_list
        print("old: ", old)
        print("base_list: ", base_list)
        base_list = func(base_list, site)
        if base_list == old:
            break
    breaking = fill_breaking_url_list(base_list, site)
    pprint(breaking)
    try:
        DB.create_db(table_name)
    except OperationalError:
        pass
    try:
        DB.update_db(breaking, table_name)
    except Exception  as e:
        print(e)


if __name__ == "__main__":
    main()