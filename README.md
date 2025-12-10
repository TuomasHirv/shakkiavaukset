# shakkiavaukset
Websovellus mihin käyttäjät voi lisätä shakkiavauksia ja kommentoida niihin.


Sovelluksessa käyttäjät pystyvät jakamaan shakkiavauksia. Avauksessa lukee siirrot ja avauksen tavoite. Tehty

Käyttäjä pystyy luomaan tunnuksen ja kirjautumaan sisään sovellukseen. Tehty

Käyttäjä pystyy lisäämään avauksia ja muokkaamaan ja poistamaan niitä.

Käyttäjä näkee sovellukseen lisätyt avaukset. Tehty

Käyttäjä pystyy etsimään avauksia hakusanalla. Tehty

Käyttäjäsivu näyttää, montako shakkiavausta käyttäjä on lisännyt ja listan käyttäjän lisäämistä avauksia. Tehty

Käyttäjä pystyy valitsemaan avaukselle yhden tai useamman luokittelun (esim. väri, agressiivinen/passiivinen).

Käyttäjä pystyy antamaan avaukselle kommentin ja Tykkaykset. Avauksessa näytetään kommentit ja Tykkäykset. Tehty
Arvosana vaihdettu tykkäykseen. 26.11


## Installation


After cloning the repository move into it.


1. Then create python virtual environmen

with 
```python3 -m venv venv```


2. Enter virtual environment (This changes depending on OS)
linux

```source venv/bin/activate```

powershell

```.\venv\Scripts\Activate.ps1```

cmd

```.\venv\Scripts\activate.bat```

git bash

```source venv/Scripts/activate```

4. INSTALL REQUIREMENTS
5. 
```pip install flask flask_wtf```

6. CREATE CONFIG.py

```cd myapp```

```touch config.py```

5. ENTER CONFIG AND CREATE A SECRET_KEY
SECRET_KEY = "123120398098HJDH"
you can change the string

6. CREATE SQL database**
   
```cd ..```

```sqlite3 database.db < schema.sql```

9. NOW RUN THE CODE IN (venv) with**


```flask run```


## Testing
per page
1. Creating a user.
- User can be created
- User creation checks for lenght of name, password and if the username is unique.
- Creation sends to login page
2. Logging in
- User can log in with correct username and password.
- log in checks for correct name and password
- Correct log in sends to homepage
3. index
- index has query with title, order by, tag specification, color specification and a search button
- below it the page shows all openings that are reached with the query.
- Openings have information (title, description, color, tag, likes, first move, second move, Link to viewer page)
- On top right there should be buttons (profile with username text, Home link to index page, New Opening link to opening creation, leaderboard link to leaderboard, log out in case of not being logged in it should have log in)
4. New opening
- Should have fields (Title, Eco code, Description, drop down Tag, drop down Color, Moves text field.
- Besides Moves there should be a short explanation of what notation is allowed.
- form checks for (Title length non emptyspace, Description lenght non empty space, Moves length and validity)
- Moves are not validated based on their possibility but rather by the correctness of the notation.
- Errors are given for all of these instead of submitting to the database when pressing Submit
- Creating an opening successfully should send to opening viewer page
5. Opening viewer
- Page should have opening information with a link to the creator.
- In the case that you created the opening you should have a button for edit opening
- Moves List and below it like button. Like button should only appear if you are logged in.
- Like button changes to Remove like if it is liked by the user
- Comments section should only appear when logged in.
- Comments section allows creating comments and liking them with the same functionality as before.
- If the user has created this opening it should have Delete opening button at the bottom
6. Comments
- Simply add information to the text field and press Send
- Comments should have username with a link to the creators page.
- if the user created the comment they should be able to edit and delete the comment
- Editing the comment removes the likes. Editing can be cancelled while editing it.
- Comment creation verifies it has data in the content
7. Editing an opening
- Pressing the edit opening should send to the opening editor.
- User is verified.
- Edit page should have (name, decription, ECO_code(not required), tag and color, and list of moves).
- Edit page verifies information like before.
- Correct edit sends back to opening viewer.
- Lets not delete our post yet
8. User page
- Press the button on top right that has your chosen username
- User page Should show (name, likes, list of openings with some information, list of comments with some information)
- Openings and comments should have a link to where you can find them.
9. Deleting an opening
- Press on the link to your opening.
- Press Delete opening
- You should get a confimation request press ok
- This should delete the opening and all associated comments and moves with the SQL CASCADE functionality.
- You should be redirected to index page with a message
10.Leaderboard
- Press the leaderboard button on the top right.
- Leaderboard page should have a list of all users ordered by like count.
- Information is (user link to user, total likes, most liked opening with link, most liked comment with link)
- If it has no information it should say None.
- Both comment and opening likes are always counted in total likes.
# That should be it for testing. There is always more to test but this list checks the most important functionalities that they broadly work.

## If i were to add something to this.
1. I would probably try to make my app.py file cleaner.
2. I would like to add a visual representation of the openings but this was more difficult than i thought since i wanst allowed to use css libraries.
3. It would also be nice if the app checked if the sequence of moves is possible in an actual chess game.
4. It would be nice to have sidelines branching off of main line openings. say Vienna game -> Vienna game falkbeer.

## Pylint report

Module app
app.py:88:8: W0622: Redefining built-in 'id' (redefined-builtin)
app.py:182:23: W0622: Redefining built-in 'id' (redefined-builtin)
app.py:201:25: W0622: Redefining built-in 'id' (redefined-builtin)
Your code has been rated at 9.60/10 (previous run: 9.85/10, -0.25)

Module siirrot_reader
myapp\siirrot_reader.py:14:0: C0301: Line too long (132/100) (line-too-long)
Your code has been rated at 9.95/10 (previous run: 9.95/10, +0.00)

I dont use the built-in id at all and since its so deep in my application i decided to not change it.

Too long line is because of sql code. I find that it is much more readable thisway however so i decided to not alter it.
