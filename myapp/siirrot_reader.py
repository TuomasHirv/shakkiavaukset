"""Functions that interact with db"""
from myapp import db
from werkzeug.security import check_password_hash

def get_openings(beginning = 0, end = 9, order = "id", query = "", color = "%", tag = "%"):
    """Queries the openings for the homepage"""
    #Note that i cant use a parameter for ORDER BY.
    #To prevent injections i created a whitelist
    whitelist = ["id", "likes", "creator"]
    tag_whitelist = ["neutral", "aggressive", "passive", "%"]
    color_whitelist = ["white", "black", "%"]
    if order not in whitelist:
        order = "id"
    m_order = "a."+order

    if color:
        if color not in color_whitelist:
            color = "%"
    if tag:
        if tag not in tag_whitelist:
            tag = "%"

    sql = f"""SELECT a.id, a.title, a.opening_description, a.likes, a.creator, a.color, a.tag, m.move_notation AS move_1, m2.move_notation AS move_2
        FROM openings AS a
        JOIN moves as m ON a.id = m.opening_id AND m.move_number = 1
        JOIN moves as m2 ON a.id = m2.opening_id AND m2.move_number = 2
        WHERE a.title LIKE ? 
        AND a.tag LIKE ? 
        AND a.color LIKE ?
        ORDER BY {m_order} DESC
        LIMIT ? OFFSET ?"""
    m_query = "%"+query+"%"

    result = db.query(sql, [m_query, tag, color, end, beginning])
    all_openings = [dict(r) for r in result]
    return all_openings


def get_moves_from_opening(opening_id):
    """Gets the moves of an opening in order"""
    sql = """SELECT m.move_number, m.move_notation
            FROM moves AS m
            WHERE m.opening_id = ?
            ORDER BY m.move_number"""
    result = db.query(sql, [opening_id,])
    moves = [dict(r) for r in result]
    return moves


def search_user_opening(username):
    """Searches all openings by a user"""
    sql = """
        SELECT id, title, opening_description, eco_code, likes
        FROM openings
        WHERE creator = ?
        ORDER BY likes DESC
    """
    return db.query(sql, [username])

def query_comments(opening_id):
    """Searcher for comments based on what opening they were submitted to"""
    sql = """
        SELECT id, creator, content, likes, likers_name
        FROM comments
        WHERE opening_id = ?
        ORDER BY likes DESC
    """
    return db.query(sql, [opening_id])

def query_by_comment_id(comment_id):
    """Searches for a comment by id"""
    sql = """
        SELECT id, creator, content, likes, likers_name, opening_id
        FROM comments
        WHERE id = ?
    """
    return db.query(sql, [comment_id,])[0]


def query_users_comments(username):
    """Searches for comments by creators username"""
    sql = """
        SELECT id, opening_id, content, likes, opening_name
        FROM comments
        WHERE creator = ?
        ORDER BY likes DESC
    """
    return db.query(sql, [username])




def opening_edit_helper(opening_id):
    """Queries all the information of the opening being edited"""
    sql = """SELECT title, opening_description, eco_code, creator, color, tag
            FROM openings 
            WHERE id = ?;"""
    opening_info = db.query(sql, [opening_id])[0]

    sql2 = """SELECT move_notation, move_number, id, color
                FROM moves
                WHERE opening_id = ?;"""
    move_info = db.query(sql2, [opening_id])
    return (opening_info, move_info)

def login_helper(username,password):
    """Checks if the given password is correct"""
    sql = "SELECT password_hash FROM users WHERE username = ?"
    password_hash = db.query(sql, [username])
    if password_hash:
        if check_password_hash(password_hash[0][0], password):
            return True
    return False


def search_for_username(username):
    """Checks if the username is already used"""
    sql = """SELECT username
            FROM users
            where username = ?"""
    if db.query(sql,[username]):
        return True
    return False


def get_opening_id(opening_id):
    """Gets opening information based on id"""
    sql = """Select a.id, a.title, a.opening_description, a.likes, a.creator, a.likers_name, a.color, a.tag
            FROM openings AS a
            Where a.id = ?"""
    result = db.query(sql, [opening_id,])
    return result[0]


def leader_board_info():
    """Sets up the information for the leader_board"""
    sql = """SELECT username, id
            FROM users"""
    users = db.query(sql)
    all_users_stats={}
    likes = 0
    for u in users:
        openings = search_user_opening(u[0])
        comments = query_users_comments(u[0])
        if openings:
            most_liked_opening = openings[0]["title"]
            most_liked_opening_id = openings[0]["id"]
        else:
            most_liked_opening = "none"
            most_liked_opening_id = -1
        if comments:
            most_liked_comment = comments[0]["content"]
            most_liked_comment_opening_id = comments[0]["opening_id"]
        else:
            most_liked_comment = "none"
            most_liked_comment_opening_id = -1
        likes = sum(o[4]for o in openings) + sum(c[3] for c in comments)
        all_users_stats[u[0]] = {
            "id": u[1],
            "name": u[0],
            "opening": most_liked_opening,
            "opening_id": most_liked_opening_id,
            "comment": most_liked_comment,
            "comment_opening_id": most_liked_comment_opening_id,
            "Total_likes":likes
        }
    return all_users_stats
