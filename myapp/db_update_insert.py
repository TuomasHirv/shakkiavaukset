"""Responsible for functions that add or update the database"""
from myapp import db, db_main, move_reader


def create_comment(creator, text, opening_id):
    """Inserts a new comment in to the database"""
    opening = db_main.get_opening_id(opening_id)

    sql = """INSERT INTO comments (opening_id, content, creator, opening_name)
            VALUES (?, ?, ?, ?)"""
    db.execute(sql, [opening_id, text, creator, opening[1]])


#Edit functions
def update_comment(comment_id, new_text):
    """Updates a pre-existing comment"""
    sql = """UPDATE comments
            SET content = ?, likes = 0, likers_name = ''
            where id = ?"""
    db.execute(sql, [new_text, comment_id])

def change_moves(move_id_new_text):
    """Changes the moves associated with an opening"""
    sql = """UPDATE moves
            SET move_notation = ?
            WHERE id = ?;"""
    for move in move_id_new_text:
        text = move[0]
        move_id = move[1]
        db.execute(sql, [text, move_id])

def change_opening_info(title, description, ecocode, opening_id, color, tag):
    """Changes the information in the opening"""
    sql = """UPDATE openings
        SET title = ?, opening_description = ?, eco_code = ?, color = ?, tag = ?
        WHERE id = ?;"""
    db.execute(sql, [title, description, ecocode, color, tag, opening_id])

def new_item_helper(name, description, eco_code, creator, moves, color, tag):
    """Creates a new opening"""
    #Creates the opening row
    sql = """INSERT INTO openings
            (title, opening_description, eco_code, likes, likers_name, creator, color, tag)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)"""
    db.execute(sql, [name, description, eco_code, 0, "", creator, color, tag])
    last_id = db.last_insert_id()
    #Adds the moves that are associated with the opening
    all_moves = move_reader.text_to_list(moves, last_id)
    sql2 = """INSERT INTO moves (opening_id, move_number, color, move_notation)
            VALUES (?, ?, ?, ?)"""
    for move in all_moves:
        db.execute(sql2, [move["opening_id"],
                          move["move_number"],
                          move["color"],
                          move["move_notation"]])
    return last_id


#Liking functions
def like(m_likes, m_likers, opening_id):
    """Adds or subtracts likes from an opening"""
    sql = """UPDATE openings
            SET likes = ?, likers_name = ?
            WHERE id = ?
            """
    db.execute(sql, [m_likes, m_likers, opening_id])

def like_comment(comment_id, likes, likers):
    """Adds or subtracts likes from a comment"""
    sql = """
        UPDATE comments SET likes = ?, likers_name = ?
        WHERE id = ?
    """
    db.execute(sql, [likes, likers, comment_id])

#Delete made most sense here
def delete_op(opening_id):
    """Deletes an opening. CASCADE makes sure that all 'children' are also deleted"""
    sql = """DELETE FROM openings WHERE id = ?"""
    db.execute(sql, [opening_id])

def delete_co(comment_id):
    """Deletes a comment"""
    sql = """DELETE FROM comments WHERE id = ?"""
    db.execute(sql, [comment_id])
