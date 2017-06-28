import requests
from bs4 import BeautifulSoup

from .uporabnik import Uporabnik

class Komentar(object):
    def __init__(self, html, seja):
        self._seja = seja
        slika = html.find("div", {"class": "avatarframe"})
        if slika:
            povezavaUporabnik = slika.find("a")
            if povezavaUporabnik and "href" in povezavaUporabnik.attrs:
                self.uporabnik = Uporabnik(self._seja, povezavaUporabnik["href"])
        self.vsebina = html.find("div", {"class": "komentarcontent"}).text
