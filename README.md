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
```python

## Installation


After cloning the repository move into it.


1. Then create python virtual environmen

with 

```python3 -m venv venv```
or 

```python -m venv venv
```

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



Pylint report

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
