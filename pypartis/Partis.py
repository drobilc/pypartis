#-*- coding: UTF-8 -*-
import requests
from bs4 import BeautifulSoup

from .Uporabnik import Uporabnik
from .Torrent import Torrent
from .Podatki import GLAVNI_URL, PRIJAVA_URL, NAPACNA_PRIJAVA_URL, BRSKAJ_URL, UPORABNIK_URL, POSTA_URL

#Kategorije in opcije za iskanje
KATEGORIJE = {"anime": 2, "eknjige": 3, "dvd-r": 4, "sport": 5, "svcd": 6, "xvid": 7, "glasba": 8, "gba": 9, "ps2": 12, "psp": 13, "xbox": 14, "tv": 17, "xxx": 18, "slike": 19, "hd": 20, "audiobook": 21, "videospoti": 23, "dokumentarci": 24, "gsm": 25, "pda": 26, "wii": 27, "ps3": 28, "ipod": 29, "risanke": 30, "hd-tv": 31, "xxx-dvd": 36, "xxx-clip": 35, "xxx-hd": 37, "sd-tv": 38}
FREELEECH = 1
DRSI = 2
MUSI = 3

class Partis(object):
    """
    Partis.si parser
    """
    def __init__(self, uporabnisko_ime, geslo):
        
        self.uporabnisko_ime = uporabnisko_ime
        #self.geslo = geslo
        
        self._seja = requests.Session()
        self._seja.headers["User-Agent"] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36"

        glava = {'Content-Type': 'application/x-www-form-urlencoded'}
        podatki = {"user[username]": uporabnisko_ime, "user[password]": geslo}
        
        #Poskusamo se prijaviti
        r = self._seja.post(PRIJAVA_URL, headers=glava, data=podatki)
        if r.url == NAPACNA_PRIJAVA_URL:
            raise PartisException("Napacno uporabnisko ime ali geslo.")

        #Uporabnika pridobimo iz piskotka (tako kot to pocne partis)
        #readCookie('udata').split('%7C');

        podatkiUporabnika = self._seja.cookies["udata"].split("%7C")
        idUporabnika = podatkiUporabnika[0]
        self.uporabnik = Uporabnik(self._seja, "/" + idUporabnika)

        #Za brezveze prenesemo /brskaj stran
        h = self._seja.get(BRSKAJ_URL)
        
        #Poiscemo podatke o prijavljenem uporabniku
        #html = BeautifulSoup(h.text, "html5lib")
        #plinkb = html.find("a", {"id": "plinkb"})
        #if plinkb and "href" in plinkb.attrs:
        #    self.uporabnik = Uporabnik(self.seja, plinkb["href"])
        
        #download = html.find("li", {"class": "download"})
        #upload = html.find("li", {"class": "upload"})
        #ratio = html.find("li", {"class": "ratio"})
        
    def iskanje(self, kljucne_besede="", stran=0, kategorije=[], moznosti=[], sortiranje=""):
        """
        Poisce vse torrente na doloceni strani
        Mozna sortiranja:
        created_at DESC - datum narascajoce
        created_at - PADAJOCE
        seeders - NARASCAJOCE
        seeders desc - PADAJOCE
        leechers - NARA
        leechers desc - PADA
        size - NARA
        size desc - PADA
        completed - NARA
        completed desc - PADA
        """
        pretvorjeneKategorije = []
        for kategorija in kategorije:
            zacasno = pretvoriVNumericnoKategorijo(kategorija)
            if zacasno:
                pretvorjeneKategorije.append(zacasno)
        moznosti = map(str, moznosti)
        parametri = {"offset": stran, "keyword": kljucne_besede, "category": ",".join(pretvorjeneKategorije), "option":",".join(moznosti), "ns":True}
        if sortiranje and len(sortiranje) > 0:
            parametri["sort"] = sortiranje
        
        glava = {"X-Requested-With": "XMLHttpRequest"}
        s = self._seja.get(BRSKAJ_URL, params=parametri, headers=glava)
        #Pretvorimo zadetke v Zadetek
        html = BeautifulSoup(s.text, "html5lib")
        self.html = html
        torrenti = html.findAll("div", {"class": "listek"})

        zadetki = []
        #Pridobimo podatke vsakega torrenta
        for torrent in torrenti:
            zadetki.append(Torrent(self._seja, torrent))

        return zadetki
