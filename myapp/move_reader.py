"""For functions that make no sense anywhere else"""
def text_to_list(moves, opening_id):
    """Changes the input from the user into a list of moves"""
    all_moves = []
    moves_list = moves.split()
    i = 1
    side = "white"
    for part in moves_list:
        line = {"opening_id": opening_id, "move_number": i, "color":side, "move_notation":part}
        all_moves.append(line)
        i+=1
        if side == "white":
            side = "black"
        else:
            side = "white"
    return all_moves
