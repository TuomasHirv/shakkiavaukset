from flask import Flask
from flask import render_template, request, session, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
import json
import sqlite3

import re

from myapp import db
from myapp import config
from myapp import siirrot_reader
SAN_PATTERN = re.compile(
    r'^(?:[KQRBN]?[a-h]?[1-8]?x?[a-h][1-8](?:=[QRBN])?|O-O(?:-O)?)([+#]?)$'
)

app = Flask(__name__)
app.secret_key = config.secret_key
@app.route("/")
def index():
    haku = request.args.get("haku", "")
    järjestys = request.args.get("jarjestys", "id")
    avaukset = siirrot_reader.hae_avauksia(0, 9, järjestys, haku)
    print(avaukset)
    return render_template("index.html", lista = avaukset, jarjestys = järjestys, haku=haku)

@app.route("/register")
def register():
    return render_template("register.html")

@app.route("/create", methods=["POST"])
def create():
    username = request.form["username"]
    password1 = request.form["password1"]
    password2 = request.form["password2"]
    if password1 != password2:
        return "VIRHE: salasanat eivät ole samat"
    password_hash = generate_password_hash(password1)

    try:
        sql = "INSERT INTO users (username, password_hash) VALUES (?, ?)"
        db.execute(sql, [username, password_hash])
    except sqlite3.IntegrityError:
        return "VIRHE: tunnus on jo varattu"

    return "Tunnus luotu"

@app.route("/login", methods=["POST"])
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
    
    tarkistus = siirrot.split()
    for move in tarkistus:
        move.strip()
        if not SAN_PATTERN.match(move):
            return f"<h1>Invalid chess move on line: {move}</h1> <a href='/new_item'> Back </a>"
    id = -1
    try:
        sql = "INSERT INTO avaukset (nimi, kuvaus, eco_code, tykkaykset, tykkaajat_nimi, tekija) VALUES (?, ?, ?, ?, ?, ?)"
        db.execute(sql, [nimi, kuvaus, eco_code, 0, "", tekija])
        id = db.last_insert_id()
    except sqlite3.IntegrityError:
        return "VIRHE: Jokin Meni pieleen"
    if (id != -1):
        #Muutetaan teksti mikä saatiin listaksi dict.
        lista = siirrot_reader.teksti_listaksi(siirrot, id)
        sql2 = "INSERT INTO moves (avaus_id, siirto_numero, color, siirto) VALUES (?, ?, ?, ?)"
        for siirto in lista:
            db.execute(sql2, [siirto["avaus_id"], siirto["siirto_numero"], siirto["color"], siirto["siirto"]])
    return redirect("/new_item")

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
    return render_template(
        "viewer.html",
        avaus=avaus,
        moves=moves,
        tykatty=tykätty
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

