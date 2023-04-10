from flask import Flask, send_from_directory


app = Flask(__name__)

# Publically available routes
@app.route('/')
def index():
    return send_from_directory('static', 'index.html')


# Run the application in Debug mode (do not use this in production
if __name__ == '__main__':
    app.run(host='0.0.0.0', port='5000', debug=True)
