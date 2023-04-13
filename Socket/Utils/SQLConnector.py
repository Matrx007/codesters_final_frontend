import mariadb
import logging

def Connect():
    try:
        conn = mariadb.connect(
            user='socket',
            password='password123',
            port=3306,
            database='socket'
        )
    except mariadb.Error as e:
        logging.error(e)

    return conn
