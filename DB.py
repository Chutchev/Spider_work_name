import sqlite3


def insert_to_db(info):
    with sqlite3.connect("URLS.db") as conn:
        for count, (url, status) in enumerate(info.items()):
            if len(status['URLS']) == 0:
                params = (count, url, 'Пустая/битая/ведет на другой ресурс')
                conn.execute("INSERT INTO CHECKEDURLS (id, url, status) values (?, ?, ?)", params)


def create_db():
    with sqlite3.connect("URLS.db") as conn:
        conn.execute("""CREATE TABLE CHECKEDURLS(
        id integer,
        url varchar(255),
        status varchar(20)
        );""")


def main():
    pass


if __name__=="__main__":
    main()