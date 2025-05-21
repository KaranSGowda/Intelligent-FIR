from flask import Flask

app = Flask(__name__)

@app.route('/')
def hello():
    return "Hello, world! This is a test Flask application."

if __name__ == '__main__':
    print("Starting test application on port 5000...")
    app.run(host='0.0.0.0', port=5000, debug=True)