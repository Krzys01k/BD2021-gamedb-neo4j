from flask import *
from neo4j import GraphDatabase, basic_auth
import hashlib
import binascii
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'C2HWGVoMGfNTBsrYQg8EcMrdTimkZfAb'
name = ""

driver = GraphDatabase.driver(
  "bolt://34.201.249.196:7687",
  auth=basic_auth("neo4j", "grant-strains-leg"))


def hash_password(password):
    """Hash a password for storing."""
    salt = hashlib.sha256(os.urandom(60)).hexdigest().encode('ascii')
    pwdhash = hashlib.pbkdf2_hmac('sha512', password.encode('utf-8'),
                                  salt, 100000)
    pwdhash = binascii.hexlify(pwdhash)
    return (salt + pwdhash).decode('ascii')


def verify_password(stored_password, provided_password):
    """Verify a stored password against one provided by user"""
    salt = stored_password[:64]
    stored_password = stored_password[64:]
    pwdhash = hashlib.pbkdf2_hmac('sha512',
                                  provided_password.encode('utf-8'),
                                  salt.encode('ascii'),
                                  100000)
    pwdhash = binascii.hexlify(pwdhash).decode('ascii')
    return pwdhash == stored_password


def get_games():
    with driver.session() as session:
        game_nodes = session.run("match (g:Game) return (g)")
        games = []
        for node in game_nodes.data():
            games.append(node['g'])

        return games

def get_game(game_title):
    with driver.session() as session:
        nodes = session.run("match (g:Game{title: '%s'}) return (g)" % game_title)
        game = nodes.data()[0]['g']
        return game
        

def get_followed(name):
    with driver.session() as session:
        followed_nodes = session.run("match (u:User)-[f:FOLLOWS]->(u2:User{name:'%s'}) return (u)" % name)
        followed = []
        for node in followed_nodes.data():
            followed.append(node['u']['name'])

        return followed

def get_following(name):
    with driver.session() as session:
        following_nodes = session.run("match (u:User)<-[f:FOLLOWS]-(u2:User{name:'%s'}) return (u)" % name)
        following = []
        for node in following_nodes.data():
            following.append(node['u']['name'])

        return following

@app.route('/')
def hello_world():
    return render_template("base.html", message="Hello !!!!", name=name)

@app.route('/games')
def games():
    games_list = get_games()
    return render_template("games.html", games=games_list, name=name)

@app.route('/games/<game_title>')
def game_details(game_title):
    global name
    # TODO: posts = get_posts(game_title)
    game = get_game(game_title)
    
    return render_template("game_details.html", name=name, game=game)




@app.route('/users', methods=['POST', 'GET'])
def users():
    global name
    message = ""
    if request.method == 'POST':
        with driver.session() as session:
            nodes = session.run("MATCH (n:User{name:'%s'}) RETURN (n)" % request.form.get("search"))
            nodes_data = nodes.data()
            if nodes_data.__len__() == 1:
                return redirect(url_for('user_details',user_name = nodes_data[0]['n']['name']))
            else:
                message = "No such User"

    return render_template("users.html", name = name, message = message)


@app.route('/users/<user_name>', methods=['POST', 'GET'])
def user_details(user_name):
    global name
    followed = get_followed(user_name)
    following = get_following(user_name)

    return render_template("user_details.html", name=name, user_name=user_name, followed=followed, following=following)


@app.route('/follow', methods=['POST'])
def follow():
    global name
    followed_name = request.form.get('follow')

    with driver.session() as session:
        session.run(
            """
            MATCH (a:User{name:'%s'}), (b:User{name:"%s"})
            where not (a) -[:FOLLOWS]->(b) 
            create (a) -[:FOLLOWS]->(b)
            """ % (name, followed_name)
        )
    return redirect(url_for('user_details', user_name=followed_name))


@app.route('/unfollow', methods=['POST'])
def unfollow():
    global name
    followed_name = request.form.get('unfollow')

    with driver.session() as session:
        session.run(
            """
            match (u:User{name:'%s'})-[f:FOLLOWS]->(u2:User{name:'%s'}) delete f
            """ % (name, followed_name)
        )
    return redirect(url_for('user_details', user_name=followed_name))

@app.route('/login', methods=['POST', 'GET'])
def login():
    global name
    message = ""

    if request.method == 'POST':
        print("login form")
        with driver.session() as session:
            nodes = session.run("MATCH (n:User{name:'%s'}) RETURN (n)" % request.form.get("name"))
            nodes_data = nodes.data()
            if nodes_data.__len__() == 1:
                user = nodes_data[0]['n']
                if verify_password(user['password'], request.form.get("password")):
                    name = request.form.get("name")
                    message = "login successful"
                else:
                    message = "login failed"
            else:
                message = "login failed"
    return render_template("login.html", name=name, message=message)


@app.route('/register', methods=['POST', 'GET'])
def register():
    global name
    message = ""

    if request.method == 'POST':
        with driver.session() as session:
            nodes = session.run("MATCH (n:User{name:'%s'}) RETURN (n)" % request.form.get("name"))
            if nodes.values().__len__() == 0:
                session.run("MERGE (n:User{name:'%s', password:'%s'}) RETURN (n)" % (request.form.get("name"), hash_password(request.form.get("password"))))
                name = request.form.get("name")
                message = "register successful"
            else:
                message = "register failed"

    return render_template("register.html", name=name, message=message)


@app.route('/logout')
def logout():
    global name
    name = ""
    return render_template("base.html", name=name, message="Logged Out")



if __name__ == '__main__':
    app.debug = True
    app.run()




