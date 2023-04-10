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
    def ValidateUsername(cur: mariadb.Cursor, Username: str):
        """Check if the given username is not already present in the database
        :param cur: mariadb cursor to use
        :param Username: username to verify
        """

        try:
            cur.execute(
                "SELECT 1 FROM Users WHERE Username=?",
                (Username,)
            )
        except mariadb.Error as e:
            logging.error(e)

        for (UserExists,) in cur:
            return False

        return True


    @staticmethod
    def ValidateEmail(cur: mariadb.Cursor, Email: str):
        """Check if the given email is not already present in the database
        :param cur: mariadb cursor to use
        :param Email: email to verify
        """

        try:
            cur.execute(
                "SELECT 1 FROM Users WHERE Email=?",
                (Email,)
            )
        except mariadb.Error as e:
            logging.error(e)

        for (EmailExists,) in cur:
            return False

        return True


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
        if not User.ValidateUsername(cur, Username):
            conn.close()
            return { "error": f"User with username '{Username}' already exists" }

        # Check if user with given email already exists
        if not User.ValidateEmail(cur, Email):
            conn.close()
            return { "error": f"User with email '{Email}' already exists'" }

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


    @staticmethod
    def Read(Username: str = '', Email: str = '', Password: str = ''):
        """Non DTO User Read method.
        Requires authenctication!
        :param Username: if this is specified authenticate using Username as user identifier
        :param Email: if this is specified authenticate using Email as user identifier
        :param Password: password to use for authentication process
        """

        conn = SQLConnector.Connect()
        cur = conn.cursor()

        # Authenticate using Username
        if Username != '':
            try:
                cur.execute(
                    "SELECT * FROM Users WHERE Username=?",
                    (Username,)
                )
            except mariadb.Error as e:
                logging.error(e)

        elif Email != '':
            try:
                cur.execute(
                    "SELECT * FROM Users WHERE Email=?",
                    (Email,)
                )
            except mariadb.Error as e:
                logging.error(e)

        else:
            conn.close()
            return { "error": "Email or username field is required" }


        for (Id,Username,CreationTimestamp,Email,PasswordHash) in cur:
            # Authenticate using bcrypt
            if not bcrypt.checkpw(Password.encode('utf-8'), PasswordHash.encode('utf-8')):
                return { "error": "Invalid password" }

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
        return { "error": "Invalid username or email" }

    
    @staticmethod
    def Update(Username='', Email='', Password='', NewUsername='', NewEmail='', NewPassword=''):
        """Update user data
        :param Username: if specified, use given username for authentication
        :param Email: if specified, use given email address for authentication
        :param Password: password to use for authentication
        :param NewUsername: if not empty update username
        :param NewEmail: if not empty update email
        :param NewPassword: if not empty update password
        """

        conn = SQLConnector.Connect()
        cur = conn.cursor()

        if Username != "":
            try:
                cur.execute(
                    "SELECT * FROM Users WHERE Username=?",
                    (Username,)
                )
            except mariadb.Error as e:
                logging.error(e)

        elif Email != "":
            try:
                cur.execute(
                    "SELECT * FROM Users WHERE Email=?",
                    (Email,)
                )
            except mariadb.Error as e:
                logging.error(e)

        else:
            conn.close()
            return { "error": "Email or username field is required" }


        user = User(0, '', 0, '', '')
        isEntry = False
        for (Id,Username,CreationTimestamp,Email,PasswordHash) in cur:
            # Authenticate
            if not bcrypt.checkpw(Password.encode('utf-8'), PasswordHash.encode('utf-8')):
                return { "error": "Invalid password" }

            if NewUsername == '':
                NewUsername = Username
            elif not User.ValidateUsername(cur, NewUsername):
                conn.close()
                return { "error": f"Cannot change username to '{NewUsername}', username already exists" }

            if NewEmail == '':
                NewEmail = Email
            elif not User.ValidateEmail(cur, NewEmail):
                conn.close()
                return { "error": f"Cannot change email to '{NewEmail}', email already exists" }

            if NewPassword == '':
                NewPassword = PasswordHash
            else:
                salt = bcrypt.gensalt()
                NewPassword = bcrypt.hashpw(NewPassword.encode('utf-8'), salt).decode('utf-8')
    
            user.Id = Id
            user.Username = NewUsername
            user.CreationTimestamp = int(time.mktime(CreationTimestamp.timetuple()))
            user.Email = NewEmail
            user.Password = NewPassword
            isEntry = True
            break

        if not isEntry:
            conn.close()
            return { "error": "Invalid username or email" }

        try:
            cur.execute(
                "UPDATE Users SET Username=?, Email=?, Password=? WHERE Id=?",
                (user.Username, user.Email, user.Password, user.Id)
            )
            conn.commit()
        except mariadb.Error as e:
            logging.error(e)
        
        conn.close()
        return user.__dict__


    @staticmethod
    def Delete(Username='', Email='', Password=''):
        """Delete given user
        :param Username: if specified, use given username for authentication
        :param Email: if specified, use given email for authentication
        :param Password: password to use for authentication
        """

        conn = SQLConnector.Connect()
        cur = conn.cursor()

        if Username != '':
            try:
                cur.execute(
                    "SELECT * FROM Users WHERE Username=?",
                    (Username,)
                )
            except mariadb.Error as e:
                logging.error(e)

        elif Email != '':
            try:
                cur.execute(
                    "SELECT * FROM Users WHERE Email=?",
                    (Email,)
                )
            except mariadb.Error as e:
                logging.error(e)
        else:
            conn.close()
            return { "error": "Email or username field is required" }


        isEntry = False
        user = User(0, '', 0, '', '')
        for (Id,Username,CreationTimestamp,Email,PasswordHash) in cur:
            user.Id = Id
            user.Username = Username
            user.CreationTimestamp = int(time.mktime(CreationTimestamp.timetuple()))
            user.Email = Email
            user.Password = PasswordHash
            isEntry = True

        if not isEntry:
            conn.close()
            return { "error": "Invalid username or email" }
        
        # Authenticate
        if not bcrypt.checkpw(Password.encode('utf-8'), user.Password.encode('utf-8')):
            conn.close()
            return { "error": "Invalid password" }

        # attempt to delete the user
        try:
            cur.execute(
                "DELETE FROM Users WHERE Id=?",
                (user.Id,)
            )
            conn.commit()
        except mariadb.Error as e:
            logging.error(e)


        conn.close()
        return user.__dict__
