#-*- coding: UTF-8 -*-
import requests
from bs4 import BeautifulSoup
import codecs

from .Podatki import GLAVNI_URL, PRIJAVA_URL, NAPACNA_PRIJAVA_URL, BRSKAJ_URL, UPORABNIK_URL, POSTA_URL
from .Uporabnik import Uporabnik
from .Komentar import Komentar

class Torrent(object):
    """
    Pridobljen torrent iz partis spletne strani
    """
    def __init__(self, seja, html):
        #self._html = html
        self._seja = seja

        self._je_ze_preneseno = False

        self.privzeteVrednosti = {
            'id': None,
            'kategorija': None,
            'naslov': None,
            'podrobno': None,
            'opis': None,
            'torrent': None,
            'velikost': None,
            'sejalci': None,
            'pijavke': None,
            'prenosi': None,
        }

        for ime in self.privzeteVrednosti:
            setattr(self, ime, self.privzeteVrednosti[ime])

        #Dobimo id torrenta in kategorijo, v katero spada
        likona = html.find("div", {"class": "likona"})
        if likona:
            if "id" in likona.attrs:
                self.id = likona["id"]
                lkategorija = likona.find("div")
                if lkategorija and "alt" in lkategorija.attrs:
                    self.kategorija = lkategorija["alt"]

        #Dobimo hiperpovezavo na podrobnosti torrenta in ime torrenta
        listeklink = html.find("div", {"class": "listeklink"})
        if listeklink:
            lnaslov = listeklink.find("a")
            if lnaslov:
                self.naslov = lnaslov.text
            if "href" in lnaslov.attrs:
                self.podrobno = GLAVNI_URL + lnaslov["href"]

        #Dobimo kratek opis torrenta
        liopis = html.find("div", {"class": "liopisl"})
        if liopis:
            self.opis = liopis.text

        #Dobimo hiperpovezavo za prenos .torrent datoteke
        torrentLink = html.find("div", {"class": "data3t"})
        if torrentLink:
            ltorrentlink = torrentLink.find("a")
            if ltorrentlink and "href" in ltorrentlink.attrs:
                self.torrent = GLAVNI_URL + ltorrentlink["href"]

        #Prenesemo se ostale podatke (velikost, stevilo sejalcev, pijavk in prenosov)
        ostaliPodatki = html.findAll("div", {"class": "datat"})
        mozni = ["velikost", "sejalci", "pijavke", "prenosi"]
        for st, div in enumerate(ostaliPodatki):
            try:
                vrednost = float(div.text)
                setattr(self, mozni[st], vrednost)
            except ValueError:
                setattr(self, mozni[st], div.text)

    def __getattr__(self, atribut):
        if not self._je_ze_preneseno:
            podatki = self.prenesiPodatke()
            self._je_ze_preneseno = True            
            for podatek in podatki:
                setattr(self, podatek, podatki[podatek])
            if atribut in podatki:
                return podatki[atribut]
            else:
                raise AttributeError()
        raise AttributeError()

    def oceni(self, ocena=5):
        glava = {"X-Requested-With": "XMLHttpRequest"}
        url = GLAVNI_URL + "/torrent/vote/{}/".format(self.id)
        parametri = {'grade': ocena}
        self._seja.get(url, params=parametri, headers=glava)

    def zahvaliSe(self):   
        url = GLAVNI_URL + "/torrent/thanks/"
        glava = {"X-Requested-With": "XMLHttpRequest"}
        parametri = {'id': self.id}
        self._seja.get(url, params=parametri, headers=glava)

    def dodajMedZaznamke(self):
        url = GLAVNI_URL + "/torrent/bookmark_add/"
        glava = {"X-Requested-With": "XMLHttpRequest"}
        parametri = {'id': self.id}
        self._seja.get(url, params=parametri, headers=glava)

    def odstraniIzZaznamkov(self):
        url = GLAVNI_URL + "/torrent/bookmark_del/"
        glava = {"X-Requested-With": "XMLHttpRequest"}
        parametri = {'id': self.id}
        self._seja.get(url, params=parametri, headers=glava)

    def komentiraj(self, komentar):
        #Mislim da podpira tudi bb kodo
        url = GLAVNI_URL + "/comment/post/"
        glava = {"X-Requested-With": "XMLHttpRequest"}
        parametri = {'torrent_id': self.id, 'msg': komentar}
        self._seja.get(url, params=parametri, headers=glava)

    def prenesiPodatke(self):
        podatki = {}
        
        u = self._seja.get(self.podrobno)
        html = u.text
        html = BeautifulSoup(html, "html5lib")

        #Pridobimo celoten naslov torrenta (prepisemo prejsnjega)
        dnaslov = html.find("div", {"class": "h11"})
        if dnaslov:
            podatki["naslov"] = dnaslov.text

        dsejalci = html.find("div", {"class": "wseeds"})
        if dsejalci:
            dnumber = dsejalci.find("a")
            if dnumber:
                try:
                    podatki["sejalci"] = float(dnumber.text)
                except ValueError:
                    pass
        
        #Pridobimo sliko torrenta
        wslika = html.find("div", {"class": "wslika"})
        if wslika:
            wimg = wslika.find("a")
            if wimg and "href" in wimg.attrs:
                podatki["slika"] = GLAVNI_URL + wimg["href"]

        dpodrobni = html.find("div", {"class": "wright"})
        dvrstice = dpodrobni.findAll("tr")
        pod = {}
        for vrstica in dvrstice:
            stolpci = vrstica.findAll("td")
            if len(stolpci) == 2:
                ime = stolpci[0].text.strip().lower().replace(" ", "_").replace(":", "").replace(u"š", "s").replace(u"č", "c").replace(u"ž", "z")
                vsebina = stolpci[1].text.strip()
                if ime == "uploader":
                    povezava = stolpci[1].find("a")['href']
                    podatki["uploader"] = Uporabnik(self._seja, povezava)
                else:
                    podatki[ime] = vsebina

        #Poiscemo komentarje
        seznamKomentarjev = []
        vsiKomentarji = html.findAll("div", {"class": "komentar"})
        if vsiKomentarji and len(vsiKomentarji) > 1:
            for komentar in vsiKomentarji[1:]:
                seznamKomentarjev.append(Komentar(komentar, self._seja))

        podatki["komentarji"] = seznamKomentarjev

        return podatki

    def prenesi(self, pot="./"):
        imeDatoteke = pot + self.id + ".torrent"
        r = self._seja.get(self.torrent, stream=True)
        with open(imeDatoteke, 'wb') as f:
            for chunk in r.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)
                    f.flush()

    def __str__(self):
        return self.naslov

    def __repr__(self):
        return "Zadetek(id: '{}')".format(self.id)
