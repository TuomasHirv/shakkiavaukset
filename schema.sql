--Käyttäjä tietokanta:
PRAGMA foreign_keys = ON;
DROP TABLE comments;
DROP TABLE moves;
DROP TABLE openings;
DROP TABLE users;


CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY,
    username TEXT UNIQUE,
    password_hash TEXT
);

--Shakkiavaus tietokanta
CREATE TABLE IF NOT EXISTS openings (
    id INTEGER PRIMARY KEY,
    title TEXT UNIQUE,
    opening_description TEXT,
    eco_code Text,
    likes INTEGER,
    likers_name Text,
    creator TEXT,
    color  TEXT,
    tag  TEXT,
    FOREIGN KEY (creator) REFERENCES users(username) ON DELETE CASCADE
);
--Shakkiavauksien siirrot atomisoidaan toiseen taulukkoon nimeltä siirrot. 
-- Niitä yhdistää avaukset.id ja siirrot.avausId
CREATE TABLE IF NOT EXISTS moves (
    id INTEGER PRIMARY KEY,
    opening_id INTEGER NOT NULL,
    move_number INTEGER NOT NULL,
    color TEXT CHECK (color IN ('white','black')),
    move_notation TEXT NOT NULL,
    FOREIGN KEY (opening_id) REFERENCES openings(id) ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS comments (
    id INTEGER PRIMARY KEY,
    opening_id INTEGER NOT NULL,
    content TEXT NOT NULL,
    creator TEXT NOT NULL,
    likes INTEGER DEFAULT 0,
    likers_name Text DEFAULT "",
    opening_name TEXT DEFAULT "",
    FOREIGN KEY (opening_id) REFERENCES openings(id) ON DELETE CASCADE
);
