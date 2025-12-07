import re
SAN_PATTERN = re.compile(
    r'^(?:[KQRBN]?[a-h]?[1-8]?x?[a-h][1-8](?:=[QRBN])?|O-O(?:-O)?)([+#]?)$'
)
def validate_username_and_password(username, password, password2):
    errors = []
    username_letters = len(re.findall(r"[A-Za-z]", username))
    password_length = len(password.replace(" ", ""))
    
    if username_letters < 5:
        errors.append("Username must contain 5 letters")
    if password_length < 6:
        errors.append("Password must have atleast 6 symbols")
    if password != password2:
        errors.append("Passwords dont match")
    return errors

def validate_new_opening(name, description, moves):
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
    return errors

def validate_opening_edit(name, description, move_updates):
    errors=[]
    name_letters = len(re.findall(r"[A-Za-z]", name))
    if name_letters < 5 or name_letters > 30:
        errors.append("Name must be between 5 and 30 letters (spaces, numbers, symbols ignored).")

    description_letters = len(re.findall(r"[A-Za-z]", description))
    if description_letters < 5 or description_letters > 60:
        errors.append("Description must be between 5 and 60 letters (spaces, numbers, symbols ignored).")
    
    for update in move_updates:
        move_text = update[1]
        if not SAN_PATTERN.match(move_text):
            errors.append(f"Invalid chess move: {move_text}")
    
    return errors
