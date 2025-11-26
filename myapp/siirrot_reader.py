from myapp import db
def teksti_listaksi(siirrot, id):
    lista = []
    siirto_lista = siirrot.split()
    i = 1
    vari = "white"
    for osa in siirto_lista:
        rivi = dict(avaus_id=id, siirto_numero =i, color = vari, siirto = osa)
        lista.append(rivi)
        i+=1
        if (vari == "white"):
            vari = "black"
        else:
           vari = "white"
    return lista

def hae_avauksia(alku = 0, loppu = 9, jarjestus = "id", haku = ""):
    m_jarjestus = "a."+jarjestus
    sql = f"""SELECT a.id, a.nimi, a.kuvaus, a.tykkaykset, a.tekija, m.siirto AS move_1, m2.siirto AS move_2
        FROM avaukset AS a
        JOIN moves as m ON a.id = m.avaus_id AND m.siirto_numero = 1
        JOIN moves as m2 ON a.id = m2.avaus_id AND m2.siirto_numero = 2
        WHERE a.nimi LIKE ?
        ORDER BY {m_jarjestus} DESC
        LIMIT ? OFFSET ?"""
    m_haku = "%"+haku+"%"
    

    result = db.query(sql, [m_haku, loppu, alku])
    lista = [dict(r) for r in result]
    return lista

def hae_avaus_id(id):
    sql = """Select a.id, a.nimi, a.kuvaus, a.tykkaykset, a.tekija, a.tykkaajat_nimi
            FROM avaukset AS a
            Where a.id = ?"""
    result = db.query(sql, [id,])
    return result[0]

def hae_siirrot_avauksesta(id):
    sql = """SELECT m.siirto_numero, m.siirto
            FROM moves AS m
            WHERE m.avaus_id = ?
            ORDER BY m.siirto_numero"""
    result = db.query(sql, [id,])
    lista = [dict(r) for r in result]
    palautus = yhdistä_siirrot(lista)
    return palautus

def yhdistä_siirrot(list):
    num = 1
    siirtoNum = 1
    ekaSiirto = ""
    ret = []
    for siirto in list:
        if num == 1:
            ekaSiirto = siirto["siirto"]
            num = 2
        else:
            rivi = dict(siirto_numero = siirtoNum, siirtoW = ekaSiirto, siirtoM = siirto["siirto"])
            ret.append(rivi)
            num = 1
            siirtoNum += 2
    if num == 2:
        rivi = dict(siirto_numero = siirtoNum, siirtoW = ekaSiirto, siirtoM = "Loss")
    return ret


def tykkää(m_tykkäykset, m_tykkääjät, id):
    sql = """UPDATE avaukset 
            SET tykkaykset = ?, tykkaajat_nimi = ?
            WHERE id = ?
            """
    db.execute(sql, [m_tykkäykset, m_tykkääjät, id])


def hae_kayttajan_avaukset(tunnus):
    sql = """
        SELECT id, nimi, kuvaus, eco_code, tykkaykset
        FROM avaukset
        WHERE tekija = ?
        ORDER BY tykkaykset DESC
    """
    return db.query(sql, [tunnus])


def tee_kommentti(tekija, teksti, avaus_id):
    sql = """INSERT INTO kommentit (avaus_id, teksti, tekija) 
            VALUES (?, ?, ?)"""
    db.execute(sql, [avaus_id, teksti, tekija])

def hae_kommentit(avaus_id):
    sql = """
        SELECT id, tekija, teksti, tykkaykset, tykkaajat_nimi
        FROM kommentit
        WHERE avaus_id = ?
        ORDER BY tykkaykset DESC
    """
    return db.query(sql, [avaus_id])

def tykkää_kommenttia(id, tykkaykset, tykkaajat):
    sql = """
        UPDATE kommentit SET tykkaykset = ?, tykkaajat_nimi = ?
        WHERE id = ?
    """
    db.execute(sql, [tykkaykset, tykkaajat, id])


def hae_kommentti_id(id):
    sql = """
        SELECT id, tekija, teksti, tykkaykset, tykkaajat_nimi, avaus_id
        FROM kommentit
        WHERE id = ?
    """
    return db.query(sql, [id,])[0]
