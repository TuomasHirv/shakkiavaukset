--Käyttäjä tietokanta:
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY,
    username TEXT UNIQUE,
    password_hash TEXT
);

--Shakkiavaus tietokanta
CREATE TABLE IF NOT EXISTS avaukset (
    id INTEGER PRIMARY KEY,
    nimi TEXT UNIQUE,
    kuvaus TEXT,
    eco_code Text,
    tykkaykset INTEGER,
    tykkaajat_nimi Text,
    tekija TEXT
);
--Shakkiavauksien siirrot atomisoidaan toiseen taulukkoon nimeltä siirrot. 
-- Niitä yhdistää avaukset.id ja siirrot.avausId
CREATE TABLE IF NOT EXISTS moves (
    id INTEGER PRIMARY KEY,
    avaus_id INTEGER NOT NULL,
    siirto_numero INTEGER NOT NULL,
    color TEXT CHECK (color IN ('white','black')),
    siirto TEXT NOT NULL,
    FOREIGN KEY (avaus_id) REFERENCES avaukset(id) ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS kommentit (
    id INTEGER PRIMARY KEY,
    avaus_id INTEGER NOT NULL,
    teksti TEXT NOT NULL,
    tekija TEXT NOT NULL,
    tykkaykset INTEGER DEFAULT 0,
    tykkaajat_nimi Text DEFAULT "",
    avauksen_nimi TEXT DEFAULT "",
    FOREIGN KEY (avaus_id) REFERENCES avaukset(id) ON DELETE CASCADE
);
CREATE TABLE moves_new (
    id INTEGER PRIMARY KEY,
    avaus_id INTEGER NOT NULL,
    siirto_numero INTEGER NOT NULL,
    color TEXT CHECK (color IN ('white','black')),
    siirto TEXT NOT NULL,
    FOREIGN KEY (avaus_id) REFERENCES avaukset(id) ON DELETE CASCADE
);

INSERT INTO moves_new SELECT * FROM moves;

DROP TABLE moves;

ALTER TABLE moves_new RENAME TO moves;

CREATE TABLE IF NOT EXISTS kommentit_new (
    id INTEGER PRIMARY KEY,
    avaus_id INTEGER NOT NULL,
    teksti TEXT NOT NULL,
    tekija TEXT NOT NULL,
    tykkaykset INTEGER DEFAULT 0,
    tykkaajat_nimi Text DEFAULT "",
    avauksen_nimi TEXT DEFAULT "",
    FOREIGN KEY (avaus_id) REFERENCES avaukset(id) ON DELETE CASCADE
);

DROP TABLE kommentit_new;