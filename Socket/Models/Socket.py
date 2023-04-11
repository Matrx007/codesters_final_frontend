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
        """Create a new tag
        :param BelongsTo: id of a socket that the tag belongs to
        :param Name: Name of the tag
        """

        conn = SQLConnector.Connect()
        cur = conn.cursor()

        # Try to insert values into the database
        try:
            cur.execute(
                "INSERT INTO Tags (BelongsTo,Name) "
                "VALUES(?, ?)",
                (BelongsTo,Name)
            )
            conn.commit()
        except mariadb.Error as e:
            logging.error(e)

        # select that value
        try:
            cur.execute(
                "SELECT * FROM Tags WHERE Id=(SELECT LAST_INSERT_ID())"
            )
        except mariadb.Error as e:
            logging.error(e)


        for (Id,BelongsTo,Name) in cur:
            tag = Tag(
                Id,
                BelongsTo,
                Name
            )
            conn.close()
            return tag.__dict__
        
        conn.close()
        return { "error": "Something went wrong" }



    @staticmethod
    def Read(BelongsTo: int):
        """Read tags that belong to certain socket
        :param BelongsTo: id of a socket that is used for query
        """

        conn = SQLConnector.Connect()
        cur = conn.cursor()

        try:
            cur.execute(
                "SELECT DISTINCT * FROM Tags WHERE BelongsTo=?",
                (BelongsTo,)
            )
        except mariadb.Error as e:
            logging.error(e)

        tags = []
        for (Id,BelongsTo,Name) in cur:
            tags.append(Tag(
                Id,
                BelongsTo,
                Name
            ).__dict__)

        conn.close()
        return tags

        
    @staticmethod
    def Delete(Id: int = 0, BelongsTo: int = 0):
        """Delete tag
        :param Id: if this value is non-zero, delete only one tag with that id
        :param BelongsTo: if this value is non-zero, delete all tags that belong to socket with id BelongsTo
        """

        conn = SQLConnector.Connect()
        cur = conn.cursor()

        if Id != 0:
            try:
                cur.execute(
                    "SELECT * FROM Tags WHERE Id=?",
                    (Id,)
                )
            except mariadb.Error as e:
                logging.error(e)

            tag = Tag(0, 0, '')
            for (Id,BelongsTo,Name) in cur:
                tag.Id = Id
                tag.BelongsTo = BelongsTo
                tag.Name = Name

            try:
                cur.execute(
                    "DELETE FROM Tags WHERE Id=?",
                    (Id,Id)
                )
                conn.commit()
            except mariadb.Error as e:
                logging.error(e)

            conn.close()
            return tag.__dict__

        elif BelongsTo != 0:
            try:
                cur.execute(
                    "SELECT * FROM Tags WHERE BelongsTo=?",
                    (BelongsTo,)
                )
            except mariadb.Error as e:
                logging.error(e)

            tags = []
            for (Id,BelongsTo,Name) in cur:
                tags.append(Tag(
                    Id,
                    BelongsTo,
                    Name
                ))

            try:
                cur.execute(
                    "DELETE FROM Tags WHERE BelongsTo=?",
                    (BelongsTo,)
                )
                conn.commit()
            except mariadb.Error as e:
                logging.error(e)


            conn.close()
            return tags

        conn.close()
        return { "error": "Id or BelongsTo must be specified in the request" }


@dataclass
class Review:
    Id: int
    BelongsTo: int
    Author: int
    Content: str
    CreationTimestamp: int
    Rating: int 


    @staticmethod
    def Create(
        BelongsTo: int,
        Author: int,
        Content: str,
        Rating: int):
        """Create a new review about the socket
        :param BelongsTo: id of a socket that is subject to the review
        :param Author: author of the review
        :param Content: string content of the review
        :param Rating: rating of the socket (R = [1;5])
        """

        conn = SQLConnector.Connect()
        cur = conn.cursor()

        if Rating < 1 or Rating > 5:
            return { "error": "Rating must be between 1 and 5" }

        try:
            cur.execute(
                "INSERT INTO Reviews (BelongsTo,Author,Content,Rating) VALUES(?,?,?,?)",
                (BelongsTo,Author,Content,Rating)
            )
            conn.commit()
        except mariadb.Error as e:
            logging.error(e)

        # Select inserted entry
        try:
            cur.execute(
                "SELECT * FROM Reviews WHERE Id=(SELECT LAST_INSERT_ID())"
            )
        except mariadb.Error as e:
            logging.error(e)


        for (Id,BelongsTo,Author,Content,CreationTimestamp,Rating) in cur:
            review = Review(
                Id,
                BelongsTo,
                Author,
                Content or '',
                int(time.mktime(CreationTimestamp.timetuple())),
                Rating
            )

            conn.close()
            return review.__dict__

        conn.close()
        return { "error": "Something went wrong when creating a review" }


    @staticmethod
    def Read(Id: int = 0, BelongsTo: int = 0):
        """Read the review
        :param Id: id of a review to query
        :param BelongsTo: socket id to query reviews for
        """

        conn = SQLConnector.Connect()
        cur = conn.cursor()

        if Id != 0:
            try:
                cur.execute(
                    "SELECT * FROM Reviews WHERE Id=?",
                    (Id,)
                )
            except mariadb.Error as e:
                logging.error(e)

            
            for (Id,BelongsTo,Author,Content,CreationTimestamp,Rating) in cur:
                review = Review(
                    Id,
                    BelongsTo,
                    Author,
                    Content or '',
                    int(time.mktime(CreationTimestamp.timetuple())),
                    Rating
                )

                conn.close()
                return review.__dict__

            conn.close()
            return { "error": "Invalid review id" }

        elif BelongsTo != 0:
            try:
                cur.execute(
                    "SELECT * FROM Reviews WHERE BelongsTo=?",
                    (BelongsTo,)
                )
            except mariadb.Error as e:
                logging.error(e)

            
            reviews = []
            for (Id,BelongsTo,Author,Content,CreationTimestamp,Rating) in cur:
                reviews.append(Review(
                    Id,
                    BelongsTo,
                    Author,
                    Content or '',
                    int(time.mktime(CreationTimestamp.timetuple())),
                    Rating
                ).__dict__)

            conn.close()
            return reviews

        conn.close()
        return { "error": "Id or BelongsTo must be specified for reading reviews" }


    @staticmethod
    def Update(Username: str, Password: str, Id: int, NewContent: str = '', NewRating: int = 0):
        """Update existing review
        :param Username: username of author to authenticate
        :param Password: password of author to authenticate
        :param Id: id of a review to update
        :param NewContent: new descriptive content of the review
        :param Rating: new rating of the review
        """


        # read the current review
        review = Review.Read(Id=Id)
        if "error" in review:
            return review

        # check the user
        user = User.Read(Username=Username, Password=Password)
        if "error" in user:
            return user

        if user['Id'] != review['Author']:
            return { "error": "Permission denied" }

        # check rating
        if NewRating < 0 or NewRating > 5:
            return { "error": "Rating must be between 1 and 5" }
        elif NewRating == 0:
            NewRating = review['Rating']

        if NewContent == '':
            NewContent = review['Content']

        conn = SQLConnector.Connect()
        cur = conn.cursor()


        # Attempt to update the entry
        try:
            cur.execute(
                "UPDATE Reviews SET Content=?, Rating=? WHERE Id=?",
                (NewContent,NewRating,Id)
            )
            conn.commit()
        except mariadb.Error as e:
            logging.error(e)

        review['Content'] = NewContent
        review['Rating'] = NewRating

        conn.close()
        return review

    
    @staticmethod
    def Delete(Username: str, Password: str, Id: int):
        """Delete the review
        :param Username: username of author to authenticate
        :param Password: password of author to authenticate
        :param Id: id of a review to delete
        """

        user = User.Read(Username=Username, Password=Password)
        if "error" in user:
            return user

        review = Review.Read(Id=Id)
        if "error" in review:
            return review

        conn = SQLConnector.Connect()
        cur = conn.cursor()

        # Attempt to delete the review
        try:
            cur.execute(
                "DELETE FROM Reviews WHERE Id=?",
                (Id,)
            )
            conn.commit()
        except mariadb.Error as e:
            logging.error(e)


        conn.close()
        return review


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
    Images: []
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


        sock = Socket.Create(Latitude, Longitude, user['Id'], user['Id'], Address, Description)
        if "error" in sock:
            return sock

        sockDTO = SocketDTO(
            sock['Id'],
            sock['Latitude'],
            sock['Longitude'],
            sock['AuthorId'],
            sock['LastEditorId'],
            sock['Address'],
            sock['Description'],
            sock['CreationTimestamp'],
            Tags,
            [],
            [],
            0
        )

        # Add tags to database
        for tag in Tags:
            createdTag = Tag.Create(BelongsTo=sock.Id, Name=tag)

            if "error" in createdTag:
                return createdTag

            sockDTO.Tags.append(createdTag)

        return sockDTO


    @staticmethod
    def ReadDTO(Id: int):
        sock = Socket.Read(Id=Id)
        if "error" in sock:
            return sock

        tags = Tag.Read(BelongsTo=Id)
        if "error" in tags:
            return tags

        reviews = Review.Read(BelongsTo=Id)
        if "error" in reviews:
            return reviews

        averageRating = 0.0

        if len(reviews):
            for review in reviews:
                averageRating = averageRating + review['Rating']

            averageRating = averageRating / float(len(reviews))

        sockDTO = SocketDTO(
            sock['Id'],
            sock['Latitude'],
            sock['Longitude'],
            sock['AuthorId'],
            sock['LastEditorId'],
            sock['Address'],
            sock['Description'],
            sock['CreationTimestamp'],
            tags,
            reviews,
            [],
            averageRating
        )

        return sockDTO.__dict__
