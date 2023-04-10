from dataclasses import dataclass

import mariadb
import logging
from Socket.Models.User import *
import Socket.Utils.SQLConnector as SQLConnector 


@dataclass
class Tag:
    Id: int
    BelongsTo: int
    Name: str

    @staticmethod
    def Create(BelongsTo: int, Name: str):
        pass

    @staticmethod
    def Read(BelongsTo: int):
        pass
        
    @staticmethod
    def Delete(Id: int):
        pass


@dataclass
class Review:
    Id: int
    BelongsTo: int
    Author: int
    Content: str
    Rating: int 


@dataclass
class Socket:
    Id: int
    Latitude: float
    Longitude: float
    AuthorId: int
    LastEditorId: int
    Address: str
    Description: str
    CreationTimestamp: int

    @staticmethod
    def Create(
        Latitude: float,
        Longitude: float,
        AuthorId: int,
        LastEditorId: int,
        Address: str,
        Description: str = ''):
        """Create a new entry to Sockets table
        :param Latitude: socket geo-location latitude
        :param Longitude: socket geo-location longitude
        :param AuthorId: author's user id
        :param LastEditorId: id of a user who last edited the information about the socket
        :param Address: string address of the location
        :param Description: description of the socket
        """

        conn = SQLConnector.Connect()
        cur = conn.cursor()

        # Insert socket into Sockets table
        try:
            cur.execute(
                "INSERT INTO Sockets (Latitude,Longitude,AuthorId,LastEditorId,Address,Description) "
                "VALUES (?,?,?,?,?,?)",
                (Latitude,Longitude,AuthorId,LastEditorId,Address,Description)
            )
            conn.commit()
        except mariadb.Error as e:
            logging.error(e)


        # Select the inserted entry
        try:
            cur.execute(
                "SELECT * FROM Sockets WHERE Id=(SELECT LAST_INSERT_ID())",
            )
        except mariadb.Error as e:
            logging.error(e)


        for (Id,Latitude,Longitude,AuthorId,LastEditorId,Address,Description,CreationTimestamp) in cur:
            sock = Socket(
                Id,
                Latitude,
                Longitude,
                AuthorId,
                LastEditorId,
                Address,
                Description or '',
                int(time.mktime(CreationTimestamp.timetuple()))
            )
            
            conn.close()
            return sock.__dict__

        conn.close()
        return { "error": "Something went wrong" }


    @staticmethod
    def Read(Id: int):
        """Read socket entry with given Id
        :param Id: socket entry id
        """

        conn = SQLConnector.Connect()
        cur = conn.cursor()

        try:
            cur.execute(
                "SELECT * FROM Sockets WHERE Id=?",
                (Id,)
            )
        except mariadb.Error as e:
            logging.error(e)


        for (Id,Latitude,Longitude,AuthorId,LastEditorId,Address,Description,CreationTimestamp) in cur:
            sock = Socket(
                Id,
                Latitude,
                Longitude,
                AuthorId,
                LastEditorId,
                Address,
                Description or '',
                int(time.mktime(CreationTimestamp.timetuple()))
            )

            return sock.__dict__

        return { "error": "Invalid socket Id" }


    @staticmethod
    def Update(
        EditorId: int,
        SocketId: int,
        NewLatitude: float = 180.0,
        NewLongitude: float = 180.0,
        NewAddress: str = '',
        NewDescription: str = ''):
        """Update existing socket
        :param EditorId: user id of a editor
        :param SocketId: Id of a socket to update
        :param NewLatitude: new latitude value; note latitude = (-90; 90)
        :param NewLongitude: new longitude value to use; note longitude = (-90; 90)
        :param NewAddress: new address description
        :param NewDescription: new description about the socket
        """

        conn = SQLConnector.Connect()
        cur = conn.cursor()

        # Read the SocketId
        try:
            cur.execute(
                "SELECT * FROM Sockets WHERE Id=?",
                (SocketId,)
            )
        except mariadb.Error as e:
            logging.error(e)

        for (Id,Latitude,Longitude,AuthorId,LastEditorId,Address,Description,CreationTimestamp) in cur:
            if NewLatitude >= 90.0 or NewLatitude <= -90.0:
                NewLatitude = Latitude
            if NewLongitude >= 90.0 or NewLongitude <= -90.0:
                NewLongitude = Longitude
            LastEditorId = EditorId
            if NewAddress == '':
                NewAddress = Address
            if NewDescription == '':
                NewDescription = Description

            sock = Socket(
                Id,
                NewLatitude,
                NewLongitude,
                AuthorId,
                LastEditorId,
                NewAddress or '',
                NewDescription or '',
                int(time.mktime(CreationTimestamp.timetuple()))
            )

            try:
                cur.execute(
                    "UPDATE Sockets SET Latitude=?, Longitude=?, LastEditorId=?, Address=?, Description=? "
                    "WHERE Id=?",
                    (NewLatitude,NewLongitude,LastEditorId,NewAddress,NewDescription,Id)
                )
                conn.commit()
            except mariadb.Error as e:
                logging.error(e)

            conn.close()
            return sock.__dict__


        conn.close()
        return { "error": "Invalid socket id" }


    @staticmethod
    def Delete(SocketId: int):
        """Delete socket entry from database
        :param SocketId: id of a socket that is going to be deleted
        """

        conn = SQLConnector.Connect()
        cur = conn.cursor()

        # Read the socket
        try:
            cur.execute(
                "SELECT * FROM Sockets WHERE Id=?",
                (SocketId,)
            )
            conn.commit()
        except mariadb.Error as e:
            logging.error(e)


        for (Id,Latitude,Longitude,AuthorId,LastEditorId,NewAddress,NewDescription,CreationTimestamp) in cur:
            sock = Socket(
                Id,
                Latitude,
                Longitude,
                AuthorId,
                LastEditorId,
                NewAddress,
                NewDescription,
                int(time.mktime(CreationTimestamp.timetuple()))
            )

            # Delete the entry
            try:
                cur.execute(
                    "DELETE FROM Sockets WHERE Id=?",
                    (SocketId,)
                )
            except mariadb.Error as e:
                logging.error(e)

            conn.close()
            return sock.__dict__

        conn.close()
        return { "error": "Invalid socket id" }



@dataclass
class SocketDTO(Socket):
    Tags: []
    Reviews: []
    AverageRating: float


    @staticmethod
    def CreateDTO(
        Username: str,
        Password: str,
        Latitude: float,
        Longitude: float,
        Address: str,
        Description: str = '',
        Tags: [] = []):
        
        # Authenticate
        user = User.Read(Username=Username, Password=Password)
        if "error" in user:
            return user


        sock = Socket.Create(Latitude, Longitude, user.Id, Address, Description)
        sockDTO = SocketDTO(
            sock.Id,
            sock.Latitude,
            sock.Longitude,
            sock.AuthorId,
            sock.Address,
            sock.Description,
            sock.CreationTimestamp,
            Tags,
            [],
            0
        )

        # Add Tags to database
        for tag in Tags:
            Tag.Create(tag['BelongsTo'], tag['Name'])

        return sockDTO
