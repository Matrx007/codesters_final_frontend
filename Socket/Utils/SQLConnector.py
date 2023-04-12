import mariadb
import logging

def Connect():
    try:
        conn = mariadb.connect(
            user='root',
            password='undefined',
            port=3306,
            database='socket'
        )
    except mariadb.Error as e:
        logging.error(e)

    return conn
