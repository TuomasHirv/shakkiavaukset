from flask import Flask, flash
from flask import render_template, request, session, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
import json
import sqlite3
from flask_wtf.csrf import CSRFProtect
import re

from myapp import db
from myapp import config
from myapp import siirrot_reader
SAN_PATTERN = re.compile(
    r'^(?:[KQRBN]?[a-h]?[1-8]?x?[a-h][1-8](?:=[QRBN])?|O-O(?:-O)?)([+#]?)$'
)

app = Flask(__name__)
app.secret_key = config.secret_key

csrf = CSRFProtect(app)

@app.route("/")
def index():
    search = request.args.get("query", "")
    order = request.args.get("order", "id")
    openings = siirrot_reader.get_openings(0, 9, order, search)
    return render_template("index.html", lista = openings, jarjestys = order, haku=search)

@app.route("/register")
def register():
    return render_template("register.html")

@app.route("/create", methods=["POST", "GET"])
def create():
    username = request.form["username"]
    password1 = request.form["password1"]
    password2 = request.form["password2"]

    username_letters = len(re.findall(r"[A-Za-z]", username))
    password_length = len(password1.replace(" ", ""))
    errors = []
    if username_letters < 5:
        errors.append("Username must contain 5 letters")
    if password_length < 6:
        errors.append("Password must have atleast 6 symbols")
    if password1 != password2:
        errors.append("Passwords dont match")
    if errors:
        flash("\n".join(errors))
        return redirect(request.referrer)
    password_hash = generate_password_hash(password1)

    try:
        sql = "INSERT INTO users (username, password_hash) VALUES (?, ?)"
        db.execute(sql, [username, password_hash])
    except sqlite3.IntegrityError:
        return "VIRHE: tunnus on jo varattu"

    return "Tunnus luotu"

@app.route("/login", methods=["POST", "GET"])
def login():
    username = request.form["username"]
    password = request.form["password"]
    
    sql = "SELECT password_hash FROM users WHERE username = ?"
    password_hash = db.query(sql, [username])[0][0]

    if check_password_hash(password_hash, password):
        session["username"] = username
        return redirect("/")
    else:
        return "VIRHE: väärä tunnus tai salasana"

@app.route("/new_item")
def new_item():
    return render_template("new_item.html")

@app.route("/create_item", methods=["POST"])
def create_item():
    name = request.form["nimi"]
    creator = session["username"]
    eco_code = request.form["eco_code"]
    description = request.form["kuvaus"]
    moves = request.form["siirrot"]
    
    errors = []
    name_letters = len(re.findall(r"[A-Za-z]", name))
    if name_letters < 5 or name_letters > 30:
        errors.append("Name must be between 5 and 30 letters (spaces, numbers, symbols ignored).")

    description_letters = len(re.findall(r"[A-Za-z]", description))
    if description_letters < 5 or description_letters > 60:
        errors.append("Description must be between 5 and 60 letters (spaces, numbers, symbols ignored).")

    moves_count = len(re.findall(r"[A-Za-z0-9]", moves))
    if moves_count < 6 or moves_count > 60:
        errors.append("Moves must be between 6 and 60 letters/numbers (spaces and symbols ignored).")
    check = moves.split()
    for move in check:
        move = move.strip()
        if not SAN_PATTERN.match(move):
            errors.append(f"Invalid chess move: {move}")
    if errors:
        for err in errors:
            flash(err)
        return redirect(url_for("new_item"))

    id = -1
    try:
        sql = "INSERT INTO avaukset (nimi, kuvaus, eco_code, tykkaykset, tykkaajat_nimi, tekija) VALUES (?, ?, ?, ?, ?, ?)"
        db.execute(sql, [name, description, eco_code, 0, "", creator])
        id = db.last_insert_id()
    except sqlite3.IntegrityError:
        return "VIRHE: Jokin Meni pieleen"
    if (id != -1):
        
        all = siirrot_reader.tekst_to_list(moves, id)
        sql2 = "INSERT INTO moves (avaus_id, siirto_numero, color, siirto) VALUES (?, ?, ?, ?)"
        for siirto in all:
            db.execute(sql2, [siirto["avaus_id"], siirto["siirto_numero"], siirto["color"], siirto["siirto"]])
        return redirect(url_for("opening_detail", opening_id=id))
    return redirect(url_for("opening_detail", opening_id=id))

@app.route("/opening/<int:opening_id>")
def opening_detail(opening_id):
    opening = siirrot_reader.get_opening_id(opening_id)
    user = session.get("username")
    liked = False
    if user in opening["tykkaajat_nimi"]:
        liked = True
    
    #print(avaus)
    moves = siirrot_reader.get_moves_from_opening(opening_id)
    #print(moves)
    comments = siirrot_reader.query_comments(opening_id)
    liked_comments = {}
    for comment in comments:
        likers = comment[4].split()
        if user in likers:
            liked_comments[comment[0]] = True
        else:
            liked_comments[comment[0]] = False

    return render_template(
        "viewer.html",
        avaus=opening,
        moves=moves,
        tykatty=liked,
        kommentit=comments,
        tykatyt=liked_comments
    )
#En käyttänyt atomisoitua dataa tykkääjien listaan ehkä virhe mutta ei isojuttu
@app.route("/opening/<int:opening_id>/tykkaa", methods=["POST"])
def tykkaa(opening_id):
    user = session.get("username")
    target = siirrot_reader.get_opening_id(opening_id)
    
    text=target["tykkaajat_nimi"]
    likers = text.split()
    if user in likers:
        likers.remove(user)
        m_likes = max(0, target["tykkaykset"]-1)
    else:
        likers.append(user)
        m_likes = target["tykkaykset"]+1
    m_text = " ".join(likers)
    siirrot_reader.like(m_likes, m_text, opening_id)
    return redirect(url_for("opening_detail", opening_id=opening_id))

@app.route("/logout")
def logout():
    del session["username"]
    return redirect("/")

@app.route("/user/<username>")
def user_profile(username):
    openings = siirrot_reader.search_user_opening(username)
    comments = siirrot_reader.query_users_comments(username)
    openings_likes = sum([a[4] for a in openings])
    comment_likes = sum([k[3] for k in comments])
    total = openings_likes+comment_likes
    return render_template("user.html", username=username, avaukset=openings, total_likes=total, kommentit=comments)

@app.route("/opening/<int:opening_id>/kommentti", methods=["POST"])
def kommentti(opening_id):
    user = session.get("username")
    if not user:
        return "Kirjaudu kommentoidaksesi"

    text = request.form["sisalto"].strip()
    if not text:
        return "Lisää sisältö"

    siirrot_reader.create_comment(user, text, opening_id)
    return redirect(url_for("opening_detail", opening_id=opening_id))


@app.route("/kommentti/<int:id>/tykkaa_kommentista", methods=["POST"])
def tykkaa_kommentista(id):
    user = session.get("username")
    target = siirrot_reader.query_by_comment_id(id)
    print(target)
    likers=target["tykkaajat_nimi"]
    list_likers = likers.split()
    if user in list_likers:
        list_likers.remove(user)
        m_likes = max(0, target["tykkaykset"]-1)
    else:
        list_likers.append(user)
        m_likes = target["tykkaykset"]+1
    m_text_likers = " ".join(list_likers)
    siirrot_reader.like_comment(id, m_likes, m_text_likers)

    return redirect(url_for("opening_detail", opening_id=target[5]))

@app.route("/comment/<int:id>/update", methods=["POST"])
def update_comment_route(id):
    new_text = request.form["new_text"]
    siirrot_reader.update_comment(id, new_text)   # your existing function
    opening_id = request.form["opening_id"]
    return redirect(url_for("opening_detail", opening_id=opening_id))

@app.route("/delete_opening/<int:opening_id>", methods=["POST"])
def delete_opening(opening_id):
    opening = siirrot_reader.get_opening_id(opening_id)
    if not opening:
        flash("Opening not found.")
        return redirect(url_for("index"))

    creator = opening[4]
    if session.get("username") != creator:
        flash("You arent allowed to remove this")
        return redirect(url_for("opening_detail", opening_id=opening_id))

    siirrot_reader.delete_op(opening_id)

    flash("Opening deleted successfully.")

    return redirect(url_for("index"))

@app.route("/delete_comment/<int:comment_id>", methods=["POST"])
def delete_comment(comment_id):
    comment = siirrot_reader.query_by_comment_id(comment_id)

    if not comment:
        flash("Comment not found")
        return redirect(url_for("index"))
    creator = comment[1]
    if session.get("username") != creator:
        flash("You are not allowed to delete this comment.")
        return redirect(request.referrer or url_for("index"))
    siirrot_reader.delete_co(comment_id)
    flash("Comment deleted successfully.")
    return redirect(request.referrer or url_for("index"))

@app.route("/leaderboard")
def leaderboard():
    users_stats = siirrot_reader.leader_board_info()

    # Sort users by Total_likes descending
    sorted_users = sorted(users_stats.values(), key=lambda x: x["Total_likes"], reverse=True)

    return render_template("leaderboard.html", users=sorted_users)
