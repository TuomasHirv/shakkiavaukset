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
    sql = """SELECT a.id, a.nimi, a.kuvaus, a.tykkaykset, a.tekija, m.siirto AS move_1, m2.siirto AS move_2
        FROM avaukset AS a
        JOIN moves as m ON a.id = m.avaus_id AND m.siirto_numero = 1
        JOIN moves as m2 ON a.id = m2.avaus_id AND m2.siirto_numero = 2
        WHERE a.nimi LIKE ?
        ORDER BY a.tykkaykset, ? 
        LIMIT ? OFFSET ?"""
    m_haku = "%"+haku+"%"
    m_jarjestus = "a."+jarjestus
    result = db.query(sql, [m_haku, m_jarjestus, loppu, alku])
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