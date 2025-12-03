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
    haku = request.args.get("haku", "")
    järjestys = request.args.get("jarjestys", "id")
    avaukset = siirrot_reader.hae_avauksia(0, 9, järjestys, haku)
    return render_template("index.html", lista = avaukset, jarjestys = järjestys, haku=haku)

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
    nimi = request.form["nimi"]
    tekija = session["username"]
    eco_code = request.form["eco_code"]
    kuvaus = request.form["kuvaus"]
    siirrot = request.form["siirrot"]
    
    errors = []
    nimi_letters = len(re.findall(r"[A-Za-z]", nimi))
    if nimi_letters < 5 or nimi_letters > 30:
        errors.append("Name must be between 5 and 30 letters (spaces, numbers, symbols ignored).")

    kuvaus_letters = len(re.findall(r"[A-Za-z]", kuvaus))
    if kuvaus_letters < 5 or kuvaus_letters > 60:
        errors.append("Description must be between 5 and 60 letters (spaces, numbers, symbols ignored).")

    siirrot_count = len(re.findall(r"[A-Za-z0-9]", siirrot))
    if siirrot_count < 6 or siirrot_count > 60:
        errors.append("Moves must be between 6 and 60 letters/numbers (spaces and symbols ignored).")

    if errors:
        for err in errors:
            flash(err)
        return redirect(url_for("new_item"))

    tarkistus = siirrot.split()
    for move in tarkistus:
        move = move.strip()
        if not SAN_PATTERN.match(move):
            errors.append(f"Invalid chess move: {move}")
    id = -1
    try:
        sql = "INSERT INTO avaukset (nimi, kuvaus, eco_code, tykkaykset, tykkaajat_nimi, tekija) VALUES (?, ?, ?, ?, ?, ?)"
        db.execute(sql, [nimi, kuvaus, eco_code, 0, "", tekija])
        id = db.last_insert_id()
    except sqlite3.IntegrityError:
        return "VIRHE: Jokin Meni pieleen"
    if (id != -1):
        
        lista = siirrot_reader.teksti_listaksi(siirrot, id)
        sql2 = "INSERT INTO moves (avaus_id, siirto_numero, color, siirto) VALUES (?, ?, ?, ?)"
        for siirto in lista:
            db.execute(sql2, [siirto["avaus_id"], siirto["siirto_numero"], siirto["color"], siirto["siirto"]])
        return redirect(url_for("opening_detail", opening_id=id))
    return redirect(url_for("opening_detail", opening_id=id))

@app.route("/opening/<int:opening_id>")
def opening_detail(opening_id):
    avaus = siirrot_reader.hae_avaus_id(opening_id)
    käyttäjä = session.get("username")
    tykätty = False
    if käyttäjä in avaus["tykkaajat_nimi"]:
        tykätty = True
    
    #print(avaus)
    moves = siirrot_reader.hae_siirrot_avauksesta(opening_id)
    #print(moves)
    kommentit = siirrot_reader.hae_kommentit(opening_id)
    tykatyt_kommentit = {}
    for kommentti in kommentit:
        lista = kommentti[4].split()
        if käyttäjä in lista:
            tykatyt_kommentit[kommentti[0]] = True
        else:
            tykatyt_kommentit[kommentti[0]] = False

    return render_template(
        "viewer.html",
        avaus=avaus,
        moves=moves,
        tykatty=tykätty,
        kommentit=kommentit,
        tykatyt=tykatyt_kommentit
    )
#En käyttänyt atomisoitua dataa tykkääjien listaan ehkä virhe mutta ei isojuttu
@app.route("/opening/<int:opening_id>/tykkaa", methods=["POST"])
def tykkaa(opening_id):
    käyttäjä = session.get("username")
    muokattava = siirrot_reader.hae_avaus_id(opening_id)
    
    teksti=muokattava["tykkaajat_nimi"]
    lista = teksti.split()
    if käyttäjä in lista:
        lista.remove(käyttäjä)
        m_tykkäykset = max(0, muokattava["tykkaykset"]-1)
    else:
        lista.append(käyttäjä)
        m_tykkäykset = muokattava["tykkaykset"]+1
    m_teksti = " ".join(lista)
    siirrot_reader.tykkää(m_tykkäykset, m_teksti, opening_id)
    return redirect(url_for("opening_detail", opening_id=opening_id))

@app.route("/logout")
def logout():
    del session["username"]
    return redirect("/")

@app.route("/user/<username>")
def user_profile(username):
    avaukset = siirrot_reader.hae_kayttajan_avaukset(username)
    kommentit = siirrot_reader.hae_kayttajan_kommentit(username)
    avaukset_likes = sum([a[4] for a in avaukset])
    kommentit_likes = sum([k[3] for k in kommentit])
    total = avaukset_likes+kommentit_likes
    return render_template("user.html", username=username, avaukset=avaukset, total_likes=total, kommentit=kommentit)

@app.route("/opening/<int:opening_id>/kommentti", methods=["POST"])
def kommentti(opening_id):
    user = session.get("username")
    if not user:
        return "Kirjaudu kommentoidaksesi"

    sisalto = request.form["sisalto"].strip()
    if not sisalto:
        return "Lisää sisältö"

    siirrot_reader.tee_kommentti(user, sisalto, opening_id)
    return redirect(url_for("opening_detail", opening_id=opening_id))


@app.route("/kommentti/<int:id>/tykkaa_kommentista", methods=["POST"])
def tykkaa_kommentista(id):
    käyttäjä = session.get("username")
    muokattava = siirrot_reader.hae_kommentti_id(id)
    print(muokattava)
    teksti=muokattava["tykkaajat_nimi"]
    lista = teksti.split()
    if käyttäjä in lista:
        lista.remove(käyttäjä)
        m_tykkäykset = max(0, muokattava["tykkaykset"]-1)
    else:
        lista.append(käyttäjä)
        m_tykkäykset = muokattava["tykkaykset"]+1
    m_teksti = " ".join(lista)
    siirrot_reader.tykkää_kommenttia(id, m_tykkäykset, m_teksti)

    return redirect(url_for("opening_detail", opening_id=muokattava[5]))


@app.route("/delete_opening/<int:opening_id>", methods=["POST"])
def delete_opening(opening_id):
    opening = siirrot_reader.hae_avaus_id(opening_id)
    if not opening:
        flash("Opening not found.")
        return redirect(url_for("index"))

    tekija = opening[4]
    if session.get("username") != tekija:
        flash("You arent allowed to remove this")
        return redirect(url_for("opening_detail", opening_id=opening_id))

    siirrot_reader.delete_op(opening_id)

    flash("Opening deleted successfully.")

    return redirect(url_for("index"))

@app.route("/delete_comment/<int:comment_id>", methods=["POST"])
def delete_comment(comment_id):
    comment = siirrot_reader.hae_kommentti_id(comment_id)

    if not comment:
        flash("Comment not found")
        return redirect(url_for("index"))
    tekija = comment[1]
    if session.get("username") != tekija:
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
