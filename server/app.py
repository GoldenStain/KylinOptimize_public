from flask import Flask

app = Flask(__name__)

@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"

@app.route("/lei/")
def say_hello():
    return "<p>Hello, lei!</p>"

def start():
		app.run(port=5000)
