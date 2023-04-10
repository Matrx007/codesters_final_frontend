from dataclasses import dataclass

import time
import mariadb
import Socket.Utils.SQLConnector as SQLConnector
import bcrypt
import logging


@dataclass
class UserDTO:
    Id: int
    Username: str
    CreationTimestamp: int

    @staticmethod
    def ReadDTO(Id: int = 0, Username: str = ""):
        """Read user as DTO (data transfer object).
        Note that either Id or Username must be specified for valid output!
        :param: if specified, read user data from database by Id
        :param Username: if specified, read user data from database by Username
        """
        conn = SQLConnector.Connect()
        cur = conn.cursor()

        if Id != 0:
            try:
                cur.execute(
                    "SELECT Id,Username,CreationTimestamp FROM Users WHERE Id=?",
                    (Id,)
                )
            except mariadb.Error as e:
                logging.error(e)
        elif Username != '':
            try:
                cur.execute(
                    "SELECT Id,Username,CreationTimestamp FROM Users WHERE Username=?",
                    (Username,)
                )
            except mariadb.Error as e:
                logging.error(e)

        for (Id,Username,CreationTimestamp) in cur:
            user = UserDTO(
                Id,
                Username,
                int(time.mktime(CreationTimestamp.timetuple()))
            )

            return user.__dict__

        return { "error": "Invalid username or user id" }



@dataclass
class User(UserDTO):
    Email: str
    Password: str


    @staticmethod
    def Create(Username: str, Email: str, Password: str):
        """Create a new user
        :param Username: username
        :param Email: email address
        :param Password: password
        """

        conn = SQLConnector.Connect()
        cur = conn.cursor()

        # Check if user with Username already exists
        try:
            cur.execute(
                "SELECT 1 FROM Users WHERE Username=?",
                (Username,)
            )
        except mariadb.Error as e:
            logging.error(e)


        for (UserExists,) in cur:
            return { "error": f"User with username '{Username}' already exists" }

        # Username should be unique, add it to the database
        salt = bcrypt.gensalt()
        pwdBytes = Password.encode('utf-8')
        h = bcrypt.hashpw(pwdBytes, salt).decode('utf-8')


        try:
            cur.execute(
                "INSERT Users (Username,Email,Password) VALUES(?, ?, ?)",
                (Username,Email,h)
            )
            conn.commit()
        except mariadb.Error as e:
            logging.error(e)


        # Select that inserted user
        try:
            cur.execute(
                "SELECT * FROM Users WHERE Id=(SELECT LAST_INSERT_ID())"
            )
        except mariadb.Error as e:
            logging.error(e)


        for (Id,Username,CreationTimestamp,Email,Password) in cur:
            user = User(
                Id,
                Username,
                int(time.mktime(CreationTimestamp.timetuple())),
                Email,
                Password
            )

            conn.close()
            return user.__dict__

        conn.close()
        return { "error": "Could not create a new user.\nTry again!" }
