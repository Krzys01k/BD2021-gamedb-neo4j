from flask import Flask, render_template  
app = Flask(__name__)


@app.route("/")
def index():
   return render_template("index.html")

@app.route("/games")
def games():
   return render_template("temp.html", content="Games")

@app.route("/people")
def people():
   return render_template("temp.html", content="People")

@app.route("/account")
def account():
   return render_template("temp.html", content="My account")

@app.route("/login")
def login():
   return render_template("temp.html", content="Log in or register")


if __name__ == '__main__':
   app.run(debug = True)

