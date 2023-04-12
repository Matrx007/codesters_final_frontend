"""Note to frontend developer:
The API is configured strictly to output data in JSON format.
This way it makes it easy to use fetch() API in Javascript, for instance, to get required data.

Request error messages are noted with "error" keys. 
Always check for them before parsing retrieved data!

Get methods use URL parameters, other methods use JSON body
"""

from flask import Flask, send_from_directory, request, session
from Socket.Models.Socket import *
from Socket.Models.User import *

app = Flask(__name__)
app.secret_key = 'password123'


# Publically available routes
@app.route('/', methods=['GET'])
def Index():
    return send_from_directory('static', 'index.html')



"""Expected JSON is:
 Username: username of the user
 Email: email of the user
 Password: password of the user
 Username and email values are mutually exclusive
"""
@app.route('/api/user/login', methods=['POST'])
def Login():
    json = request.get_json()

    session['Password'] = json['Password']
    if 'Email' in json:
        session['Email'] = json['Email']
        return User.Read(Email=json['Email'], Password=json['Password'])
    elif 'Username' in json:
        session['Username'] = json['Username']
        return User.Read(Username=json['Username'], Password=json['Password'])

    return User.Read()



"""Expected JSON is:
 Username: username of the user
 Email: email of the user
 Password: password of the user
 Username and email values are mutually exclusive
"""
@app.route('/api/user/register', methods=['POST'])
def Register():
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


"""Expected JSON is:
 Username: username of the user
 Email: email of the user
 Password: password of the user
 Username and email values are mutually exclusive
"""
@app.route('/api/user/logout', methods=['POST'])
def Logout():
    session.pop('Username', None)
    session.pop('Password', None)

    return redirect('/')


"""Expected URL arguments are:
 Id: Id of the user
 Username: username of the user
"""
@app.route('/api/user', methods=['GET'])
def GetUser():
    Id = request.args.get('Id') or 0
    Username = request.args.get('Username')

    print(f"{Id}: {Username}")

    return User.ReadDTO(Id=Id, Username=Username)


"""Expected JSON is:
 Username: username of the user
 Email: email of the user
 Password: password of the user
 NewUsername: <optional>
 NewEmail: <optional>
 NewPassword: <optional>
"""
@app.route('/api/user', methods=['PUT'])
def UpdateUser():
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




# Run the application in Debug mode (do not use this in production
if __name__ == '__main__':
    app.run(host='0.0.0.0', port='5000', debug=True)
