"""Note to frontend developer:
The API is configured strictly to output data in JSON format.
This way it makes it easy to use fetch() API in Javascript, for instance, to get required data.

Request error messages are noted with "error" keys. 
Always check for them before parsing retrieved data!
"""

from flask import Flask, send_from_directory
import Models


app = Flask(__name__)


# Publically available routes
@app.route('/')
def index():
    return send_from_directory('static', 'index.html')


# Run the application in Debug mode (do not use this in production
if __name__ == '__main__':
    app.run(host='0.0.0.0', port='5000', debug=True)
