"""This is router for the web-application"""
import sqlite3

from flask import Flask, flash
from flask import render_template, request, session, redirect, url_for
from werkzeug.security import generate_password_hash
from flask_wtf.csrf import CSRFProtect

from myapp import db, config, siirrot_reader, text_validation, db_update_insert
app = Flask(__name__)
app.secret_key = config.SECRET_KEY

csrf = CSRFProtect(app)

@app.route("/")
def index():
    """Page shows either log in or the default search page of the application"""
    search = request.args.get("query", "")
    order = request.args.get("order", "id")
    tag = request.args.get("tag", "%")
    color = request.args.get("color", "%")
    openings = siirrot_reader.get_openings(0, 20, order, search, color, tag)
    return render_template("index.html", opening_list = openings, order = order, query=search,)

@app.route("/register")
def register():
    """Only holds the template for registering"""
    return render_template("register.html")

@app.route("/create", methods=["POST", "GET"])
def create():
    """Handles creating the new account"""
    username = request.form["username"]
    password1 = request.form["password1"]
    password2 = request.form["password2"]
    #Checking if the text is valid
    errors = text_validation.validate_username_and_password(username, password1, password2)
    if errors:
        flash("\n".join(errors))
        return redirect(url_for("register"))

    password_hash = generate_password_hash(password1)
    try:
        sql = "INSERT INTO users (username, password_hash) VALUES (?, ?)"
        db.execute(sql, [username, password_hash])
    except sqlite3.IntegrityError:
        flash("VIRHE: tunnus on jo varattu")
        return redirect(url_for("register"))

    return redirect(url_for("index"))

@app.route("/login", methods=["POST", "GET"])
def login():
    """Recieves the user credentials and handles log-in"""
    username = request.form["username"]
    password = request.form["password"]


    if siirrot_reader.login_helper(username, password):
        session["username"] = username
        return redirect("/")
    flash("VIRHE: väärä tunnus tai salasana")
    return redirect(request.referrer)

@app.route("/new_item")
def new_item():
    """Template for creating a new opening"""
    return render_template("new_item.html")

@app.route("/create_item", methods=["POST"])
def create_item():
    """Handles creating the new opening"""
    name = request.form["nimi"]
    creator = session["username"]
    eco_code = request.form["eco_code"]
    description = request.form["kuvaus"]
    moves = request.form["siirrot"]
    tag = request.form["tag"]
    color = request.form["color"]
    #Checking if the text is valid
    errors = text_validation.validate_new_opening(name,description,moves)
    if errors:
        for err in errors:
            flash(err)
        return redirect(request.referrer)
    try:
        opening_id = db_update_insert.new_item_helper(name, description, eco_code, creator, moves, color, tag)
    except sqlite3.IntegrityError:
        flash("VIRHE: Jokin Meni pieleen")
        return redirect(request.referrer)

    return redirect(url_for("opening_detail", opening_id=opening_id))

@app.route("/opening/<int:opening_id>")
def opening_detail(opening_id):
    """Shows the opening the comments and blends it with user info"""
    opening = siirrot_reader.get_opening_id(opening_id)
    user = session.get("username")
    liked = False
    if user in opening["likers_name"]:
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
    """Handles liking an opening"""
    user = session.get("username")
    target = siirrot_reader.get_opening_id(opening_id)

    text=target["likers_name"]
    likers = text.split()
    if user in likers:
        likers.remove(user)
        m_likes = max(0, target["likes"]-1)
    else:
        likers.append(user)
        m_likes = target["likes"]+1
    m_text = " ".join(likers)
    db_update_insert.like(m_likes, m_text, opening_id)
    return redirect(url_for("opening_detail", opening_id=opening_id))

@app.route("/logout")
def logout():
    """Handles a log out request"""
    del session["username"]
    return redirect("/")

@app.route("/user/<username>")
def user_profile(username):
    """Shows user information"""
    openings = siirrot_reader.search_user_opening(username)
    comments = siirrot_reader.query_users_comments(username)
    total = sum(k[3] for k in comments) + sum(a[4] for a in openings)

    info = {"openings":openings,"total_likes":total,"comments":comments}
    return render_template("user.html", username=username, info=info)

@app.route("/opening/<int:opening_id>/kommentti", methods=["POST"])
def kommentti(opening_id):
    """Handles creating the comments"""
    user = session.get("username")
    errors = []
    if not user:
        errors.append("You arent logged in")


    text = request.form["sisalto"].strip()
    if not text:
        errors.append("Add content to the comment")

    if errors:
        for err in errors:
            flash(err)
            return redirect(request.referrer)


    db_update_insert.create_comment(user, text, opening_id)
    return redirect(url_for("opening_detail", opening_id=opening_id))


@app.route("/kommentti/<int:id>/tykkaa_kommentista", methods=["POST"])
def tykkaa_kommentista(id):
    """Handles liking a comment"""
    user = session.get("username")
    target = siirrot_reader.query_by_comment_id(id)
    print(target)
    likers=target["likers_name"]
    list_likers = likers.split()
    if user in list_likers:
        list_likers.remove(user)
        m_likes = max(0, target["likes"]-1)
    else:
        list_likers.append(user)
        m_likes = target["likes"]+1
    m_text_likers = " ".join(list_likers)
    db_update_insert.like_comment(id, m_likes, m_text_likers)

    return redirect(url_for("opening_detail", opening_id=target[5]))

@app.route("/comment/<int:id>/update", methods=["POST"])
def update_comment_route(id):
    """This handles updating comments"""
    comment = siirrot_reader.query_by_comment_id(id)
    if not comment:
        flash("Comment not found")
        return redirect(url_for("index"))
    creator = comment[1]
    if session.get("username") != creator:
        flash("You are not allowed to delete this comment.")
        return redirect(request.referrer or url_for("index"))

    new_text = request.form["new_text"]

    text = new_text.strip()
    if not text:
        flash("Add content to the comment")
        return redirect(request.referrer)

    db_update_insert.update_comment(id, new_text)   # your existing function
    opening_id = request.form["opening_id"]
    return redirect(url_for("opening_detail", opening_id=opening_id))

@app.route("/delete_opening/<int:opening_id>", methods=["POST"])
def delete_opening(opening_id):
    """Handles deleting openings"""
    opening = siirrot_reader.get_opening_id(opening_id)
    if not opening:
        flash("Opening not found.")
        return redirect(url_for("index"))

    creator = opening[4]
    if session.get("username") != creator:
        flash("You arent allowed to remove this")
        return redirect(url_for("opening_detail", opening_id=opening_id))

    db_update_insert.delete_op(opening_id)

    flash("Opening deleted successfully.")

    return redirect(url_for("index"))

@app.route("/delete_comment/<int:comment_id>", methods=["POST"])
def delete_comment(comment_id):
    """Handles deleting comments"""
    comment = siirrot_reader.query_by_comment_id(comment_id)

    if not comment:
        flash("Comment not found")
        return redirect(url_for("index"))
    creator = comment[1]
    if session.get("username") != creator:
        flash("You are not allowed to delete this comment.")
        return redirect(request.referrer or url_for("index"))
    db_update_insert.delete_co(comment_id)
    flash("Comment deleted successfully.")
    return redirect(request.referrer or url_for("index"))

@app.route("/leaderboard")
def leaderboard():
    """Shows leaderboard information"""
    users_stats = siirrot_reader.leader_board_info()

    # Sort users by Total_likes descending
    sorted_users = sorted(users_stats.values(), key=lambda x: x["Total_likes"], reverse=True)

    return render_template("leaderboard.html", users=sorted_users)

@app.route("/edit_opening/<int:opening_id>")
def edit_opening(opening_id):
    """Page that allows users to edit openings"""
    info = siirrot_reader.opening_edit_helper(opening_id)
    info = {"opening": info[0],"moves": info[1], "opening_id":opening_id}
    return render_template("edit_opening.html", info=info)

@app.route("/edit_opening/<int:opening_id>", methods=["POST"])
def save_opening_edit(opening_id):
    """Handles editing openings"""
    opening = siirrot_reader.get_opening_id(opening_id)
    user = session.get("username")
    if opening[4] != user:
        flash("You arent allowed to change that opening")
        redirect(request.referrer)

    title = request.form["nimi"]
    description = request.form["kuvaus"]
    eco_code = request.form["eco_code"]
    tag = request.form["tag"]
    color = request.form["color"]
    move_updates = []
    for key, value in request.form.items():
        if key.startswith("siirto_"):
            move_id = int(key.split("_")[1])
            move_text = value.strip()
            move_updates.append((move_id, move_text))

    errors = text_validation.validate_opening_edit(title, description, move_updates)
    if errors:
        for err in errors:
            flash(err)
            return redirect(request.referrer)


    db_update_insert.change_opening_info(title, description, eco_code, opening_id, color, tag)
    db_update_insert.change_moves(move_updates)
    return redirect(url_for("opening_detail", opening_id=opening_id))
