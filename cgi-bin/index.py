import cgi
import subprocess
import sqlite3


def select_all_into_db(table_name):
    with sqlite3.connect("URLS.db") as conn:
        cur = conn.cursor()
        data = cur.execute(f"SELECT * FROM {table_name}")
        strokes = data.fetchall()
    return strokes


def main():
    form = cgi.FieldStorage()
    url = form.getfirst("URL")
    table_name = url.split("/")[2].split('.')
    table_name = "_".join(table_name).replace('-', '__')
    subprocess.call(f"python script.py {url}")
    strokes = select_all_into_db(table_name)
    print("Content-type: text/html\n")
    print("""<!DOCTYPE HTML>
                    <html>
                    <head>
                        <meta charset="windows-1251">
                        <title>Результаты</title>
                    </head>
                    <body>""")
    print('<div id="header"><h1>Вывод</h1></div>')
    for url, status, date in strokes:
        print(f'<p>URL: <a href="{url}">{url}</a>    Статус: {status}    Дата: {date}</p>')
    print('/body')


if __name__ == '__main__':
    main()
