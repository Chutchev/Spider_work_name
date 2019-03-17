import sqlite3
import datetime

def select_into_db(url, table_name):
    with sqlite3.connect("URLS.db") as conn:
        cur = conn.cursor()
        data = cur.execute(f"SELECT * FROM {table_name} WHERE url='{url}'")
        stroke = data.fetchall()
    if len(stroke) > 0:
        return True
    else:
        return False


def update_db(info, table_name):
    with sqlite3.connect("URLS.db") as conn:
        cur = conn.cursor()
        for url in info:
            if url is not None:
                if select_into_db(url, table_name):
                    cur.execute(f"""UPDATE {table_name} SET url={url}, status='Пустая/неработающая ссылка', 
                    last_check={datetime.date.today()}""")
                else:
                    insert_to_db(url, 'Пустая/неработающая ссылка', table_name)


def insert_to_db(url, status, table_name):
    with sqlite3.connect("URLS.db") as conn:
        last_check = datetime.date.today()
        conn.execute(f"INSERT INTO {table_name} (url, status, last_check) VALUES (?, ?, ?)", (url, status, last_check))


def create_db(table_name):
    with sqlite3.connect("URLS.db") as conn:
        conn.execute(f"""CREATE TABLE {table_name}(
        url varchar(1000),
        status varchar(255),
        last_check DATE
        );""")


def main():
    pass


if __name__ == "__main__":
    main()
