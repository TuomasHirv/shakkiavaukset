from flask import Flask
from flask import render_template, request, session, redirect
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3

from myapp import db
from myapp import config
from myapp import siirrot_reader

app = Flask(__name__)
app.secret_key = config.secret_key
@app.route("/")
def index():
    return render_template("index.html")

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

    id = -1
    try:
        sql = "INSERT INTO avaukset (nimi, kuvaus, eco_code, tykkaykset, tekija) VALUES (?, ?, ?, ?, ?)"
        db.execute(sql, [nimi, kuvaus, eco_code, 0, tekija])
        id = db.last_insert_id()
    except sqlite3.IntegrityError:
        return "VIRHE: Jokin Meni pieleen"
    if (id != -1):
        #Muutetaan teksti mikä saatiin listaksi dict.
        lista = siirrot_reader.teksti_listaksi(siirrot, id)
        sql2 = "INSERT INTO moves (avaus_id, siirto_numero, color, siirto) VALUES (?, ?, ?, ?)"
        for siirto in lista:
            db.execute(sql2, [siirto["avaus_id"], siirto["siirto_numero"], siirto["color"], siirto["siirto"]])
    return lista




@app.route("/logout")
def logout():
    del session["username"]
    return redirect("/")

