#-*- coding: UTF-8 -*-
import requests
from bs4 import BeautifulSoup

from .podatki import PRIJAVA_URL, UPORABNIK_URL, POSTA_URL
from .sporocilo import Sporocilo

class Uporabnik(object):
    """Uporabnik na portalu Partis"""

    def __init__(self, seja, _id):
        self.id = _id
        self.url = UPORABNIK_URL + self.id
        self._seja = seja
        self._je_ze_preneseno = False

    def prenesiPodatke(self):
        r = self._seja.get(self.url)
        html = BeautifulSoup(r.text, "html5lib")

        podatki = {}

        wslika = html.find("div", {"class": "wslika"})
        if wslika:
            wurl = wslika.find("img")
            if wurl and "src" in wurl.attrs:
                podatki["slika"] = UPORABNIK_URL + wurl['src']

        dpodrobni = html.find("div", {"class": "wright"})
        dvrstice = dpodrobni.findAll("tr")
        for vrstica in dvrstice:
            stolpci = vrstica.findAll("td")
            if len(stolpci) == 2:
                ime = stolpci[0].text.strip().lower().replace(" ", "_").replace(":", "").replace(u"š", "s").replace(u"č", "c").replace(u"ž", "z")
                vsebina = stolpci[1].text.strip()
                podatki[ime] = vsebina
        
        return podatki

    def __getattr__(self, atribut):
        if not self._je_ze_preneseno:
            podatki = self.prenesiPodatke()
            self._je_ze_preneseno = True
            
            for podatek in podatki:
                setattr(self, podatek, podatki[podatek])
            
            if atribut in podatki:
                return podatki[atribut]

        raise AttributeError()

    def posljiSporocilo(self, zadeva, sporocilo):
        """Posiljanje sporocil temu uporabniku"""
        url = GLAVNI_URL + "/profil/sendmsg/"
        glava = {"X-Requested-With": "XMLHttpRequest"}
        parametri = {'to': self.uporabnisko_ime, 'subject': zadeva, 'msg': sporocilo}
        self._seja.get(url, params=parametri, headers=glava)

    def prenesiSporocila(self):
        """Prenos sporocil, ki jih ima ta uporabnik"""
        r = self._seja.get(POSTA_URL)
        html = BeautifulSoup(r.text, "html5lib")
        postaContainer = html.find("div", {"id": "inbox"})        
        seznamSporocilUl = postaContainer.find("ul", {"class": "linklist"})
        elementi = seznamSporocilUl.findAll("li")

        sporocila = []
        for element in elementi:
            slikaS = element.find("img")
            idSporocila = slikaS["id"]
            sporocila.append(Sporocilo(self._seja, idSporocila))

        return sporocila
