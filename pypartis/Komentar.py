import requests
from bs4 import BeautifulSoup
import re

from .uporabnik import Uporabnik

class Komentar(object):
	"""Komentar pri torrentu na Partis.si"""

	def __init__(self, seja):
		self._seja = seja

	def izHtml(self, html):
		slika = html.find("div", {"class": "avatarframe"})
		if slika:
			povezavaUporabnik = slika.find("a")
			if povezavaUporabnik and "href" in povezavaUporabnik.attrs:
				zadetki = re.match(r"\/uporabnik\/(\d+)", povezavaUporabnik["href"])
				if zadetki:
					uporabnikId = zadetki.group(1)
					self.uporabnik = Uporabnik(self._seja, uporabnikId)
		self.vsebina = html.find("div", {"class": "komentarcontent"}).text
