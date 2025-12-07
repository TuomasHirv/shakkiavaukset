from myapp import db
def tekst_to_list(moves, id):
    all = []
    moves_list = moves.split()
    i = 1
    side = "white"
    for osa in moves_list:
        line = dict(avaus_id=id, siirto_numero =i, color = side, siirto = osa)
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
    whitelist = ["id", "tykkaykset", "tekija"]
    if order not in whitelist:
        order = "id"
    m_order = "a."+order

    sql = f"""SELECT a.id, a.nimi, a.kuvaus, a.tykkaykset, a.tekija, m.siirto AS move_1, m2.siirto AS move_2
        FROM avaukset AS a
        JOIN moves as m ON a.id = m.avaus_id AND m.siirto_numero = 1
        JOIN moves as m2 ON a.id = m2.avaus_id AND m2.siirto_numero = 2
        WHERE a.nimi LIKE ?
        ORDER BY {m_order} DESC
        LIMIT ? OFFSET ?"""
    m_query = "%"+query+"%"

    result = db.query(sql, [m_query, end, beginning])
    all = [dict(r) for r in result]
    return all

def get_opening_id(id):
    sql = """Select a.id, a.nimi, a.kuvaus, a.tykkaykset, a.tekija, a.tykkaajat_nimi
            FROM avaukset AS a
            Where a.id = ?"""
    result = db.query(sql, [id,])
    return result[0]

def get_moves_from_opening(id):
    sql = """SELECT m.siirto_numero, m.siirto
            FROM moves AS m
            WHERE m.avaus_id = ?
            ORDER BY m.siirto_numero"""
    result = db.query(sql, [id,])
    moves = [dict(r) for r in result]
    palautus = connect_moves(moves)
    return palautus


def connect_moves(moves):
    num = 1
    moveNum = 1
    firstMove = ""
    ret = []
    for move in moves:
        if num == 1:
            firstMove = move["siirto"]
            num = 2
        else:
            rivi = dict(siirto_numero = moveNum, siirtoW = firstMove, siirtoM = move["siirto"])
            ret.append(rivi)
            num = 1
            moveNum += 2
    if num == 2:
        rivi = dict(siirto_numero = moveNum, siirtoW = firstMove, siirtoM = "Loss")
    return ret


def like(m_likes, m_likers, id):
    sql = """UPDATE avaukset 
            SET tykkaykset = ?, tykkaajat_nimi = ?
            WHERE id = ?
            """
    db.execute(sql, [m_likes, m_likers, id])

def search_user_opening(username):
    sql = """
        SELECT id, nimi, kuvaus, eco_code, tykkaykset
        FROM avaukset
        WHERE tekija = ?
        ORDER BY tykkaykset DESC
    """
    return db.query(sql, [username])

def create_comment(creator, tekst, opening_id):
    avaus = get_opening_id(opening_id)

    sql = """INSERT INTO kommentit (avaus_id, teksti, tekija, avauksen_nimi) 
            VALUES (?, ?, ?, ?)"""
    db.execute(sql, [opening_id, tekst, creator, avaus[1]])
def query_comments(opening_id):
    sql = """
        SELECT id, tekija, teksti, tykkaykset, tykkaajat_nimi
        FROM kommentit
        WHERE avaus_id = ?
        ORDER BY tykkaykset DESC
    """
    return db.query(sql, [opening_id])

def like_comment(id, likes, likers):
    sql = """
        UPDATE kommentit SET tykkaykset = ?, tykkaajat_nimi = ?
        WHERE id = ?
    """
    db.execute(sql, [likes, likers, id])

def query_by_comment_id(id):
    sql = """
        SELECT id, tekija, teksti, tykkaykset, tykkaajat_nimi, avaus_id
        FROM kommentit
        WHERE id = ?
    """
    return db.query(sql, [id,])[0]

def update_comment(id, new_text):
    sql = """UPDATE kommentit 
            SET teksti = ?, tykkaykset = 0, tykkaajat_nimi = ''
            where id = ?"""
    db.execute(sql, [new_text, id])


def query_users_comments(username):
    sql = """
        SELECT id, avaus_id, teksti, tykkaykset, avauksen_nimi
        FROM kommentit
        WHERE tekija = ?
        ORDER BY tykkaykset DESC
    """
    return db.query(sql, [username])


def delete_op(id):
    sql = """DELETE FROM avaukset WHERE id = ?"""
    db.execute(sql, [id])

def delete_co(id):
    sql = """DELETE FROM kommentit WHERE id = ?"""
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
            most_liked_opening = openings[0]["nimi"]
            most_liked_opening_id = openings[0]["id"]
        else:
            most_liked_opening = "none"
            most_liked_opening_id = -1
        if comments:
            most_liked_comment = comments[0]["teksti"]
            most_liked_comment_opening_id = comments[0]["avaus_id"]
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
    sql = """SELECT nimi, kuvaus, eco_code, tekija
            FROM avaukset 
            WHERE id = ?;"""
    opening_info = db.query(sql, [opening_id])[0]

    sql2 = """SELECT siirto, siirto_numero, id, color
                FROM moves
                WHERE avaus_id = ?;"""
    move_info = db.query(sql2, [opening_id])
    return (opening_info, move_info)

def change_moves(move_id_new_text):
    sql = """UPDATE moves 
            SET siirto = ?
            WHERE id = ?;"""
    for move in move_id_new_text:
        text = move[0]
        id = move[1]
        db.execute(sql, [text, id])

def change_opening_info(title, description, ecocode, id):
    sql = """UPDATE avaukset 
        SET nimi = ?, kuvaus = ?, eco_code = ?
        WHERE id = ?;"""
    db.execute(sql, [title, description, ecocode, id])