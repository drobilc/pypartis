#-*- coding: UTF-8 -*-
import requests
from bs4 import BeautifulSoup
import codecs
import datetime

from .podatki import GLAVNI_URL, PRIJAVA_URL, NAPACNA_PRIJAVA_URL, BRSKAJ_URL, UPORABNIK_URL, POSTA_URL
from .uporabnik import Uporabnik
from .komentar import Komentar

class Torrent(object):
    """Torrent objekt iz Partis spletne strani"""
    def __init__(self, seja, id=None):
        self._seja = seja
        self._je_ze_preneseno = False

        self.id = id

        # Nastavimo privzete vrednosti objekta
        privzeteVrednosti = {
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
            'datum': None
        }

        for ime in privzeteVrednosti:
            setattr(self, ime, privzeteVrednosti[ime])

    def izHtml(self, html):
        """Ustvari torrent objekt iz html"""
        # Najdemo kdaj je bil torrent nalozen
        if "ctime" in html.attrs:
            unix_ustvarjen = int(html["ctime"])
            self.datum = datetime.datetime.fromtimestamp(unix_ustvarjen)

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
                vrednost = int(div.text)
                setattr(self, mozni[st], vrednost)
            except ValueError:
                setattr(self, mozni[st], div.text)

    def __getattr__(self, atribut):
        # Ce podatki torrenta se niso bili preneseni, jih prenesi
        if not self._je_ze_preneseno:
            podatki = self.prenesiPodatke()
            self._je_ze_preneseno = True            
            for podatek in podatki:
                setattr(self, podatek, podatki[podatek])

            if atribut in podatki:
                return podatki[atribut]

        raise AttributeError()

    def oceni(self, ocena=5):
        """Oceni torrent z ustrezno oceno"""
        glava = {"X-Requested-With": "XMLHttpRequest"}
        url = GLAVNI_URL + "/torrent/vote/{}/".format(self.id)
        parametri = {'grade': ocena}
        self._seja.get(url, params=parametri, headers=glava)

    def zahvaliSe(self):
        """Zahvali se za nalozen torrent"""
        url = GLAVNI_URL + "/torrent/thanks/"
        glava = {"X-Requested-With": "XMLHttpRequest"}
        parametri = {'id': self.id}
        self._seja.get(url, params=parametri, headers=glava)

    def dodajMedZaznamke(self):
        """Doda torrent med zaznamke uporabnika"""
        url = GLAVNI_URL + "/torrent/bookmark_add/"
        glava = {"X-Requested-With": "XMLHttpRequest"}
        parametri = {'id': self.id}
        self._seja.get(url, params=parametri, headers=glava)

    def odstraniIzZaznamkov(self):
        """Odstrani torrent iz zaznamkov uporabnika"""
        url = GLAVNI_URL + "/torrent/bookmark_del/"
        glava = {"X-Requested-With": "XMLHttpRequest"}
        parametri = {'id': self.id}
        self._seja.get(url, params=parametri, headers=glava)

    def komentiraj(self, komentar):
        """Komentira torrent (podpira bb kodo)"""
        url = GLAVNI_URL + "/comment/post/"
        glava = {"X-Requested-With": "XMLHttpRequest"}
        parametri = {'torrent_id': self.id, 'msg': komentar}
        self._seja.get(url, params=parametri, headers=glava)

    def prenesiPodatke(self):
        """Prenese podatke torrenta"""
        podatki = {}
        
        u = self._seja.get(self.podrobno)
        html = BeautifulSoup(u.text, "html5lib")

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

        #Poiscemo komentarje in jih shranimo pod self.komentarji
        seznamKomentarjev = []
        vsiKomentarji = html.findAll("div", {"class": "komentar"})
        if vsiKomentarji and len(vsiKomentarji) > 1:
            for komentarHtml in vsiKomentarji[1:]:
                trenutniKomentar = Komentar(self._seja)
                trenutniKomentar.izHtml(komentarHtml)
                seznamKomentarjev.append(trenutniKomentar)

        podatki["komentarji"] = seznamKomentarjev

        return podatki

    def prenesi(self, pot="./"):
        """Prenese torrent v ustrezno mapo z imenom ID.torrent"""
        imeDatoteke = pot + self.id + ".torrent"
        r = self._seja.get(self.torrent, stream=True)
        with open(imeDatoteke, 'wb') as f:
            for chunk in r.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)
                    f.flush()