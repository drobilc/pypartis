#-*- coding: UTF-8 -*-
import requests
from bs4 import BeautifulSoup

from .Podatki import POSTA_URL

class Sporocilo(object):
    """
    Sporocilo, ki ga uporabnik poslje oziroma prejme
    """
    def __init__(self, seja, _id):

        if _id.startswith("pi"):
            _id = _id.replace("pi", "")
        self.id = _id
        self._seja = seja
        self._je_ze_preneseno = False

    def prenesiPodatke(self):
        url = "http://www.partis.si/profil/msg/?id={}".format(self.id)
        r = self._seja.get(url)
        html = r.text
        html = BeautifulSoup(html, "html5lib")
        podatki = {}

        tabela = html.find("table")
        if tabela:
            vrstice = tabela.findAll("tr")
            for vrstica in vrstice:
                stolpci = vrstica.findAll("td")
                if len(stolpci) == 2:
                    ime = stolpci[0].text.strip().lower().replace(" ", "_").replace(":", "").replace(u"š", "s").replace(u"č", "c").replace(u"ž", "z")
                    vsebina = stolpci[1].text.strip()
                    podatki[ime] = vsebina
                    if ime == "posiljatelj":
                        povezava = stolpci[1].find("a")["href"]
                        podatki[ime] = povezava

        sporociloC = html.find("div", {"class": "postamsg"})
        if sporociloC:
            podatki["sporocilo"] = sporociloC.text.strip()

        return podatki

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

    def izbrisi(self):
        url = "http://www.partis.si/profil/delmsg/{}".format(self.id)
        glava = {"X-Requested-With": "XMLHttpRequest"}
        self._seja.get(url, headers=glava)
