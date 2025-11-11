

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