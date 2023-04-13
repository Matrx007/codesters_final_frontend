"""Note to frontend developer:
The API is configured strictly to output data in JSON format.
This way it makes it easy to use fetch() API in Javascript, for instance, to get required data.

Request error messages are noted with "error" keys. 
Always check for them before parsing retrieved data!

Get methods use URL parameters, other methods use JSON body
"""

from flask import Flask, send_from_directory, request, session, redirect
from Socket.Models.Socket import *
from Socket.Models.User import *

app = Flask(__name__)
app.secret_key = 'password123'


# Publically available routes
@app.route('/', methods=['GET'])
def Index():
    return send_from_directory('static', 'index.html')

"""API routes for user model"""


@app.route('/api/user/login', methods=['POST'])
def Login():
    """Expected JSON is:
     Username: username of the user
     Email: email of the user
     Password: password of the user
     Username and email values are mutually exclusive
    """
    json = request.get_json()

    session['Password'] = json['Password']
    if 'Email' in json:
        session['Email'] = json['Email']
        return User.Read(Email=json['Email'], Password=json['Password'])
    elif 'Username' in json:
        session['Username'] = json['Username']
        return User.Read(Username=json['Username'], Password=json['Password'])

    return User.Read()



@app.route('/api/user/register', methods=['POST'])
def Register():
    """Expected JSON is:
     Username: username of the user
     Email: email of the user
     Password: password of the user
     Username and email values are mutually exclusive
    """
    json = request.get_json()
    session['Password'] = json['Password']

    Username = ''
    Email = ''
    Password = ''
    if 'Username' in json:
        Username = json['Username']
    if 'Email' in json:
        Email = json['Email']
    if 'Password' in json:
        Password = json['Password']

    user = User.Create(Username=Username, Email=json['Email'], Password=json['Password'])

    if not "error" in user:
        session['Username'] = user['Username']

    return user


@app.route('/api/user/logout', methods=['POST'])
def Logout():
    """Expected JSON is:
     Username: username of the user
     Email: email of the user
     Password: password of the user
     Username and email values are mutually exclusive
    """
    session.pop('Username', None)
    session.pop('Password', None)

    return redirect('/')


@app.route('/api/user', methods=['GET'])
def GetUser():
    """Expected URL arguments are:
     Id: Id of the user
     Username: username of the user
    """
    Id = request.args.get('Id') or 0
    Username = request.args.get('Username')

    print(f"{Id}: {Username}")

    return User.ReadDTO(Id=Id, Username=Username)


@app.route('/api/user', methods=['PUT'])
def UpdateUser():
    """Expected JSON is:
     Username: username of the user
     Email: email of the user
     Password: password of the user
     NewUsername: <optional>
     NewEmail: <optional>
     NewPassword: <optional>
    """
    json = request.get_json()
    
    Username = ''
    Password = json['Password']
    NewUsername = ''
    NewEmail = ''
    NewPassword = ''

    if 'Username' in json:
        Username = json['Username']
    if 'Email' in json:
        Email = json['Email']
    if 'NewUsername' in json:
        NewUsername = json['NewUsername']
    if 'NewEmail' in json:
        NewEmail = json['NewEmail']
    if 'NewPassword' in json:
        NewPassword = json['NewPassword']

    user = User.Update(
        Username=session['Username'],
        Password=session['Password'],
        NewUsername=NewUsername,
        NewEmail=NewEmail,
        NewPassword=NewPassword
    )

    if NewUsername != '':
        session['Username'] = NewUsername
    if NewPassword != '':
        session['Password'] = NewPassword

    return user


@app.route('/api/user', methods=['DELETE'])
def DeleteUser():
    return User.Delete(Username=session['Username'], Password=session['Password'])


""" API routes for Tag model """

@app.route('/api/tag', methods=['GET'])
def GetTags():
    """Expected URL arguments are:
     BelongsTo: id of a socket that owns the tags
    """

    BelongsTo = request.args.get('BelongsTo') or 0
    return Tag.Read(BelongsTo)


@app.route('/api/tag', methods=['POST'])
def CreateTag():
    """Expected json is:
     BelongsTo: id of a socket that owns given tag
     Name: name of the tag
    """

    json = request.json


    if 'BelongsTo' in json:
        BelongsTo = json['BelongsTo']
    if 'Name' in json:
        Name = json['Name']

    return Tag.Create(BelongsTo, Name)

@app.route('/api/tag', methods=['DELETE'])
def DeleteTag():
    """Expected json is:
     BelongsTo: id of a socket that owns tags that are going to be deleted
     Id: id of a single tag that will be deleted
    """

    json = request.json
    BelongsTo = 0
    Id = 0

    if 'BelongsTo' in json:
        BelongsTo = json['BelongsTo']
    if 'Id' in json:
        Id = json['Id']

    return Tag.Delete(Id, BelongsTo)


""" API routes for Review model """

@app.route('/api/review', methods=['GET'])
def GetReviews():
    """Expected URL arguments are:
     Id: id of a review that will be returned
     BelongsTo: id of a socket whose reviews will be returned
    """

    Id = request.args.get('Id') or 0
    BelongsTo = request.args.get('BelongsTo') or 0

    return Review.Read(Id, BelongsTo)

@app.route('/api/review', methods=['POST'])
def PostReview():
    """Expected json is:
     BelongsTo: id of socket to associate this review with
     Author: id of the author of the review
     Content: content of the review
     Rating: rating of the review (R = [1;5])
    """

    json = request.json
    BelongsTo = 0
    Author = 0
    Content = ''
    Rating = 0

    if 'BelongsTo' in json:
        BelongsTo = json['BelongsTo']
    if 'Author' in json:
        Author = json['Author']
    if 'Content' in json:
        Content = json['Content']
    if 'Rating' in json:
        Rating = json['Rating']

    return Review.Create(
        BelongsTo,
        Author,
        Content,
        Rating
    )


@app.route('/api/review', methods=['PUT'])
def UpdateReview():
    """Expected json is:
     Id: id of a review to update
     NewContent: new descriptive review content
     NewRating: new rating for the review
    """

    json = request.json

    Username = ''
    Password = ''

    if 'Username' in session:
        Username = session['Username']
    if 'Password' in session:
        Password = session['Password']

    Id = 0
    NewContent = ''
    NewRating = 0

    if 'Id' in json:
        Id = json['Id']
    if 'NewContent' in json:
        NewContent = json['NewContent']
    if 'NewRating' in json:
        NewRating = json['NewRating']

    return Review.Update(Username, Password, Id, NewContent, NewRating)


@app.route('/api/review', methods=['DELETE'])
def DeleteReview():
    """Expected json is:
     Id: id of a review that is going to be deleted
    """

    json = request.json

    Username = ''
    Password = ''

    if 'Username' in session:
        Username = session['Username']
    if 'Password' in session:
        Password = session['Password']

    Id = 0

    if 'Id' in json:
        Id = json['Id']

    return Review.Delete(Username, Password, Id)




""" API routes for Socket model"""

@app.route('/api/socket', methods=['GET'])
def GetSocket():
    """Expected URL arguments are:
     Id: Id of a socket to query
     BottomLeftLongitude: longitude of bottom left coordinate from 2D map
     BottomLeftLatitude: latitude of bottom left coordinate from 2D map
     TopRightLongitude: longitude of top right coordinate from 2D map
     TopRightLatitude: latitude of top right coordinate from 2D map

     NOTE: Id and coordinate parameters are mutually exclusive
    """
    
    Id = request.args.get('Id') or 0
    BottomLeftLongitude = float(request.args.get('BottomLeftLongitude') or 180)
    BottomLeftLatitude = float(request.args.get('BottomLeftLatitude') or 180)
    TopRightLongitude = float(request.args.get('TopRightLongitude') or 180)
    TopRightLatitude = float(request.args.get('TopRightLatitude') or 180)
    
    return SocketDTO.ReadDTO(
        Id=Id,
        BottomLeft=(BottomLeftLongitude,BottomLeftLatitude),
        TopRight=(TopRightLongitude,TopRightLatitude)
    )

@app.route('/api/socket', methods=['POST'])
def PostSocket():
    """Expected json is:
     Latitude: latitude of the socket
     Longitude: longitude of the socket
     Address: address description of the socket
     Description: general description of the socket
    """
    json = request.json
    
    Username = ''
    Password = ''

    if 'Username' in session:
        Username = session['Username']
    if 'Password' in session:
        Password = session['Password']

    Latitude = float(json['Latitude'])
    Longitude = float(json['Longitude'])
    Address = json['Address']
    Description = json['Description']
    Tags = []

    if 'Tags' in json:
        Tags = json['Tags']

    return SocketDTO.CreateDTO(
        Username,
        Password,
        Latitude,
        Longitude,
        Address,
        Description,
        Tags
    )

@app.route('/api/socket', methods=['PUT'])
def UpdateSocket():
    """Expected json is:
     SocketId: id of a socket
     NewLatitude: new latitude of the socket <optional>
     NewLongitude: new longitude of the socket <optional>
     NewAddress: new address description of the socket <optional>
     NewDescription: new general description of the socket <optional>
    """
    json = request.json

    Username = ''
    Password = ''

    if 'Username' in session:
        Username = session['Username']
    if 'Password' in session:
        Password = session['Password']

    user = User.Read(Username=Username, Password=Password)

    if 'error' in user:
        return user

    SocketId = 0
    NewLatitude = 180.0
    NewLongitude = 180.0
    NewAddress = ''
    NewDescription = ''

    if 'SocketId' in json:
        SocketId = json['SocketId']
    if 'NewLatitude' in json:
        NewLatitude = json['NewLatitude']
    if 'NewLongitude' in json:
        NewLongitude = json['NewLongitude']
    if 'NewAddress' in json:
        NewAddress = json['NewAddress']
    if 'NewDescription' in json:
        NewDescription = json['NewDescription']

    return Socket.Update(
        user['Id'],
        SocketId,
        NewLatitude,
        NewLongitude,
        NewAddress,
        NewDescription
    )


@app.route('/api/socket', methods=['DELETE'])
def DeleteSocket():
    """Expected json is:
     SocketId: id of the socket that is going to be deleted
    """
    json = request.json

    Username = ''
    Password = ''
    SocketId = 0
    
    if 'SocketId' in json:
        SocketId = json['SocketId']

    if 'Username' in session:
        Username = session['Username']
    if 'Password' in session:
        Password = session['Password']

    print(f'{Username}: {Password}')
    user = User.Read(Username=Username, Password=Password)
    if "error" in user:
        return user

    return Socket.Delete(SocketId)




# Run the application in Debug mode (do not use this in production
if __name__ == '__main__':
    app.run(host='0.0.0.0', port='5000', debug=True)
