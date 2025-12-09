from myapp import db
from werkzeug.security import generate_password_hash, check_password_hash
def tekst_to_list(moves, id):
    all = []
    moves_list = moves.split()
    i = 1
    side = "white"
    for osa in moves_list:
        line = dict(opening_id=id, move_number =i, color = side, move_notation = osa)
        all.append(line)
        i+=1
        if (side == "white"):
            side = "black"
        else:
           side = "white"
    return all

def get_openings(beginning = 0, end = 9, order = "id", query = ""):
    #Tässä kannattaa huomioda, että ORDER BY osiota ei voi parametrisoida. Joten olen päättänyt whitelistata osan syötteistä.
    #Tällä tavoin estän SQL injektion koodiin.
    whitelist = ["id", "likes", "creator"]
    if order not in whitelist:
        order = "id"
    m_order = "a."+order

    sql = f"""SELECT a.id, a.title, a.opening_description, a.likes, a.creator, m.move_notation AS move_1, m2.move_notation AS move_2
        FROM openings AS a
        JOIN moves as m ON a.id = m.opening_id AND m.move_number = 1
        JOIN moves as m2 ON a.id = m2.opening_id AND m2.move_number = 2
        WHERE a.title LIKE ?
        ORDER BY {m_order} DESC
        LIMIT ? OFFSET ?"""
    m_query = "%"+query+"%"

    result = db.query(sql, [m_query, end, beginning])
    all = [dict(r) for r in result]
    return all

def get_opening_id(id):
    sql = """Select a.id, a.title, a.opening_description, a.likes, a.creator, a.likers_name
            FROM openings AS a
            Where a.id = ?"""
    result = db.query(sql, [id,])
    return result[0]

def get_moves_from_opening(id):
    sql = """SELECT m.move_number, m.move_notation
            FROM moves AS m
            WHERE m.opening_id = ?
            ORDER BY m.move_number"""
    result = db.query(sql, [id,])
    moves = [dict(r) for r in result]
    return moves


def connect_moves(moves):
    num = 1
    moveNum = 1
    firstMove = ""
    ret = []
    for move in moves:
        if num == 1:
            firstMove = move["move_notation"]
            num = 2
        else:
            rivi = dict(move_number = moveNum, moveW = firstMove, moveM = move["move_notation"])
            ret.append(rivi)
            num = 1
            moveNum += 2
    if num == 2:
        rivi = dict(siirto_numero = moveNum, siirtoW = firstMove, siirtoM = "Loss")
    return ret


def like(m_likes, m_likers, id):
    sql = """UPDATE openings 
            SET likes = ?, likers_name = ?
            WHERE id = ?
            """
    db.execute(sql, [m_likes, m_likers, id])

def search_user_opening(username):
    sql = """
        SELECT id, title, opening_description, eco_code, likes
        FROM openings
        WHERE creator = ?
        ORDER BY likes DESC
    """
    return db.query(sql, [username])

def create_comment(creator, text, opening_id):
    opening = get_opening_id(opening_id)

    sql = """INSERT INTO comments (opening_id, content, creator, opening_name) 
            VALUES (?, ?, ?, ?)"""
    db.execute(sql, [opening_id, text, creator, opening[1]])
def query_comments(opening_id):
    sql = """
        SELECT id, creator, content, likes, likers_name
        FROM comments
        WHERE opening_id = ?
        ORDER BY likes DESC
    """
    return db.query(sql, [opening_id])

def like_comment(id, likes, likers):
    sql = """
        UPDATE comments SET likes = ?, likers_name = ?
        WHERE id = ?
    """
    db.execute(sql, [likes, likers, id])

def query_by_comment_id(id):
    sql = """
        SELECT id, creator, content, likes, likers_name, opening_id
        FROM comments
        WHERE id = ?
    """
    return db.query(sql, [id,])[0]

def update_comment(id, new_text):
    sql = """UPDATE comments 
            SET content = ?, likes = 0, likers_name = ''
            where id = ?"""
    db.execute(sql, [new_text, id])


def query_users_comments(username):
    sql = """
        SELECT id, opening_id, content, likes, opening_name
        FROM comments
        WHERE creator = ?
        ORDER BY likes DESC
    """
    return db.query(sql, [username])


def delete_op(id):
    sql = """DELETE FROM openings WHERE id = ?"""
    db.execute(sql, [id])

def delete_co(id):
    sql = """DELETE FROM comments WHERE id = ?"""
    db.execute(sql, [id])


def leader_board_info():
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
        likes = sum(o[4]for o in openings) + sum([c[3] for c in comments])
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


def opening_edit_helper(opening_id):
    sql = """SELECT title, opening_description, eco_code, creator
            FROM openings 
            WHERE id = ?;"""
    opening_info = db.query(sql, [opening_id])[0]

    sql2 = """SELECT move_notation, move_number, id, color
                FROM moves
                WHERE opening_id = ?;"""
    move_info = db.query(sql2, [opening_id])
    return (opening_info, move_info)

def change_moves(move_id_new_text):
    sql = """UPDATE moves 
            SET move_notation = ?
            WHERE id = ?;"""
    for move in move_id_new_text:
        text = move[0]
        id = move[1]
        db.execute(sql, [text, id])

def change_opening_info(title, description, ecocode, id):
    sql = """UPDATE openings 
        SET title = ?, opening_description = ?, eco_code = ?
        WHERE id = ?;"""
    db.execute(sql, [title, description, ecocode, id])


def login_helper(username,password):
    sql = "SELECT password_hash FROM users WHERE username = ?"
    password_hash = db.query(sql, [username])[0][0]

    if check_password_hash(password_hash, password):
        return True
    else:
        return False

def new_item_helper(name, description, eco_code, creator, moves):
    sql = """INSERT INTO openings (title, opening_description, eco_code, likes, likers_name, creator) 
            VALUES (?, ?, ?, ?, ?, ?)"""
    db.execute(sql, [name, description, eco_code, 0, "", creator])
    id = db.last_insert_id()

    all = tekst_to_list(moves, id)
    sql2 = "INSERT INTO moves (opening_id, move_number, color, move_notation) VALUES (?, ?, ?, ?)"
    for move in all:
        db.execute(sql2, [move["opening_id"], move["move_number"], move["color"], move["move_notation"]])
    return id


def search_for_username(username):
    sql = """SELECT username
            FROM users
            where username = ?"""
    if db.query(sql,[username]):
        return True
    else:
        return False
    