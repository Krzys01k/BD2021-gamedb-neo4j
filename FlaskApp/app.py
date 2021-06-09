from flask import *
from neo4j import GraphDatabase, basic_auth
from os import *

app = Flask(__name__)
app.config['SECRET_KEY'] = 'C2HWGVoMGfNTBsrYQg8EcMrdTimkZfAb'
name = ""

driver = GraphDatabase.driver(
  "bolt://34.201.249.196:7687",
  auth=basic_auth("neo4j", "grant-strains-leg"))


def get_games():
    with driver.session() as session:
        game_nodes = session.run("match (g:Game) return (g)")
        games = []
        for node in game_nodes.data():
            games.append(node['g'])

        return games


@app.route('/')
def hello_world():
    return render_template("base.html", message="Hello !!!!", name=name)

@app.route('/games')
def games():
    games_list = get_games()
    return render_template("games.html", games=games_list, name=name)


@app.route('/login', methods=['POST', 'GET'])
def login():
    global name
    message = ""

    if request.method == 'POST':
        print("login form")
        with driver.session() as session:
            nodes = session.run("MATCH (n:User{email:'%s', password:'%s'}) RETURN (n)" % (request.form.get("email"), request.form.get("passwd")))
            print("MATCH (n:User{email:'%s', password:'%s'}) RETURN (n)" % (request.form.get("email"), request.form.get("passwd")))
            # print(nodes.values().__len__())
            # for i in range(-100,100):
            #     if nodes.values().__len__() == i:
            #         print("len is", i)
            if nodes.values().__len__() == 1:
                name = request.form.get("email")
                message = "login successful"
            else:
                message = "login failed"


    return render_template("login.html", name=name, message=message)


@app.route('/register', methods=['POST', 'GET'])
def register():
    global name
    message = ""

    if request.method == 'POST':
        with driver.session() as session:
            nodes = session.run("MATCH (n:User{email:'%s'}) RETURN (n)" % request.form.get("email"))
            # print(nodes.values().__len__())
            # for i in range(-100,100):
            #     if nodes.values().__len__() == i:
            #         print("len is", i)
            if nodes.values().__len__() == 0:
                session.run("MERGE (n:User{email:'%s', password:'%s'}) RETURN (n)" % (request.form.get("email"), request.form.get("passwd")))
                name = request.form.get("email")
                message = "register successful"
            else:
                message = "register failed"

    return render_template("register.html", name=name, message=message)


@app.route('/logout')
def logout():
    global name
    name = ""
    flash("Logged Out")
    return render_template("base.html", name=name, message="Logged Out")


if __name__ == '__main__':
    app.debug = True
    app.run()




