#-*- coding: UTF-8 -*-
import requests
from bs4 import BeautifulSoup

from .uporabnik import Uporabnik
from .torrent import Torrent
from .podatki import GLAVNI_URL, PRIJAVA_URL, NAPACNA_PRIJAVA_URL, BRSKAJ_URL, UPORABNIK_URL, POSTA_URL

#Kategorije in opcije za iskanje
KATEGORIJE = {"anime": 2, "eknjige": 3, "dvd-r": 4, "sport": 5, "svcd": 6, "xvid": 7, "glasba": 8, "gba": 9, "ps2": 12, "psp": 13, "xbox": 14, "tv": 17, "xxx": 18, "slike": 19, "hd": 20, "audiobook": 21, "videospoti": 23, "dokumentarci": 24, "gsm": 25, "pda": 26, "wii": 27, "ps3": 28, "ipod": 29, "risanke": 30, "hd-tv": 31, "xxx-dvd": 36, "xxx-clip": 35, "xxx-hd": 37, "sd-tv": 38}
FREELEECH = 1
DRSI = 2
MUSI = 3

class Partis(object):
    """Partis.si scraper"""
    def __init__(self, uporabnisko_ime, geslo):
        
        self.uporabnisko_ime = uporabnisko_ime
        
        self._seja = requests.Session()
        self._seja.headers["User-Agent"] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36"

        glava = {'Content-Type': 'application/x-www-form-urlencoded'}
        podatki = {"user[username]": uporabnisko_ime, "user[password]": geslo}
        
        # Prijavimo se na Partis.si
        r = self._seja.post(PRIJAVA_URL, headers=glava, data=podatki)
        if r.url == NAPACNA_PRIJAVA_URL:
            raise PartisException("Napacno uporabnisko ime ali geslo.")

        # Podatke uporabnika dobimo iz piskotka
        podatkiUporabnika = self._seja.cookies["udata"].split("%7C")
        idUporabnika = podatkiUporabnika[0]
        self.uporabnik = Uporabnik(self._seja, idUporabnika)

        # Posljemo zahtevo na /brskaj, sicer ne moremo prenasati podatkov
        h = self._seja.get(BRSKAJ_URL)
        
    def iskanje(self, kljucne_besede="", stran=0, kategorije=[], moznosti=[], sortiranje=""):
        """Najdemo torrente z ustreznimi parametri"""

        # Ce navedemo nepravilno sortiranje torrentov, se to ponastavi na privzeto
        if sortiranje not in ["", "created_at desc", "created_at", "seeders", "seeders desc", "leechers", "leechers desc", "size", "size desc", "completed", "completed desc"]:
            sortiranje = ""

        # Kategorije posredujemo v numericni obliki
        pretvorjeneKategorije = []
        for kategorija in kategorije:
            if kategorija in KATEGORIJE:
                pretvorjeneKategorije.append(KATEGORIJE[kategorija])

        moznosti = map(str, moznosti)
        parametri = {"offset": stran, "keyword": kljucne_besede, "category": ",".join(pretvorjeneKategorije), "option":",".join(moznosti), "ns":True}
        if sortiranje and len(sortiranje) > 0:
            parametri["sort"] = sortiranje
        
        # Sestavimo poizvedbo
        glava = {"X-Requested-With": "XMLHttpRequest"}
        s = self._seja.get(BRSKAJ_URL, params=parametri, headers=glava)

        # Prenesemo html in v njem najdemo ustrezne torrente
        html = BeautifulSoup(s.text, "html5lib")
        najdeniTorrenti = html.findAll("div", {"class": "listek"})

        # Iz htmlja izvlecemo podatke o torrentih
        zadetki = []
        for torrentHtml in najdeniTorrenti:
            trenutniTorrent = Torrent(self._seja)
            trenutniTorrent.izHtml(torrentHtml)
            zadetki.append(trenutniTorrent)

        return zadetki
