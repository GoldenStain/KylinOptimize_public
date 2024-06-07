from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')
@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"
@app.route("/lei/")
def say_hello():
    return "<p>Hello, lei!</p>"

if __name__ == "main":
    app.run(debug=True)