from flask import *
from neo4j import GraphDatabase, basic_auth
import hashlib
import binascii
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'C2HWGVoMGfNTBsrYQg8EcMrdTimkZfAb'
name = ""

driver = GraphDatabase.driver(
  "bolt://3.227.247.75:7687",
  auth=basic_auth("neo4j", "mint-baths-mathematics"))


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


def add_review_to_db(author_name, game_title, score, content):
    with driver.session() as session:
        session.run(
            """
            match (u:User{name:'%s'}), (g:Game{title:'%s'})
            where not (u)-[:WROTE]->()-[:ADDRESSES]->(g)
            merge (u)-[f:WROTE]->(r:Review{score:%s, content:'%s'})-[f2:ADDRESSES]->(g)
            return f, f2, u, g, r
            """ % (author_name, game_title, score, content)
        )
    return


def review_exists(author_name, game_title):
    with driver.session() as session:
        nodes = session.run(
            """
            match (u:User{name:'%s'}), (g:Game{title:'%s'})
            where  (u)-[:WROTE]->()-[:ADDRESSES]->(g)
            return (u)
            """ % (author_name, game_title)
        )
        if nodes.values().__len__() != 0:
            return 1
        return 0

def get_reviews():
    with driver.session() as session:
        nodes = session.run("match (u:User)-[:WROTE]->(r:Review)-[:ADDRESSES]->(g:Game) \
            return u.name as name, r.score as score, r.content as content, g.title as title")
        reviews = []

        nodes_data = nodes.data()
        for i in range(len(nodes_data)):
            reviews.append(nodes_data[i])

        return reviews


def get_user_reviews(user_name):
    with driver.session() as session:
        nodes = session.run(
            """
            match (u:User{name:'%s'}), (r:Review), (g:Game)
            where  (u)-[:WROTE]->(r)-[:ADDRESSES]->(g)
            return (r), (g)
            """ % user_name
        )
        reviews = []

        for n in nodes:
            review = {
                'game': n['g']['title'],
                'score': n['r']['score'],
                'content': n['r']['content']
            }
            reviews.append(review)

        return reviews


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
    all_reviews = get_reviews()
    game_reviews = list(filter(lambda d: d['title'] in [game_title], all_reviews))
    print(game_reviews)
    game = get_game(game_title)
    rev_exists = True
    if name:
        rev_exists = review_exists(name, game.get('title'))
    
    return render_template("game_details.html", name=name, game=game, rev_exists=rev_exists, reviews=game_reviews)


@app.route('/add_review/<game_title>', methods=['POST', 'GET'])
def add_review_form(game_title):
    global name
    if request.method == 'POST':
        add_review_to_db(name, game_title, request.form.get('score'), request.form.get('content'))
        return redirect(url_for('game_details', game_title=game_title))

    return render_template("add_review.html", name=name, game_title=game_title)

@app.route('/reviews')
def reviews():
    reviews = get_reviews()
    return render_template("reviews.html", reviews=reviews, name=name)


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
    reviews = get_user_reviews(user_name)

    return render_template("user_details.html", name=name, user_name=user_name, followed=followed, following=following, reviews=reviews)


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
        with driver.session() as session:
            nodes = session.run("MATCH (n:User{name:'%s'}) RETURN (n)" % request.form.get("name"))
            nodes_data = nodes.data()
            if nodes_data.__len__() == 1:
                user = nodes_data[0]['n']
                if verify_password(user['password'], request.form.get("password")):
                    name = request.form.get("name")
                    return redirect('/login_success')
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
                return redirect('/register_success')
            else:
                message = "register failed"

    return render_template("register.html", name=name, message=message)


@app.route('/logout')
def logout():
    global name
    name = ""
    return render_template("base.html", name=name, message="Logged Out")


@app.route('/register_success')
def register_success():
    global name
    return render_template("base.html", name=name, message="Register Successful")


@app.route('/login_success')
def login_success():
    global name
    return render_template("base.html", name=name, message="Login Successful")


if __name__ == '__main__':
    app.debug = True
    app.run()




