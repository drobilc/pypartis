# pypartis
partis.si website scraper.

## Uporaba
Preden lahko uporabljamo pypartis scraper ga je potrebno namestiti na svoj računalnik. To lahko storimo tako, da si prenesemo Github repozitorij in postavimo mapo `pypartis` v mapo v kateri imamo trenuten projekt.
Za to lahko uporabimo ukaz `git clone https://github.com/drobilc/pypartis`.

Ravno tako lahko modul namestimo s sledečimi ukazi
```
git clone https://github.com/drobilc/pypartis
cd pypartis
python setup.py install
```

Ko je modul nameščen, ga je potrebno v projektu vključiti. To storimo tako, da na vrh Python skripte dodamo spodnjo vrstico.
```python
from pypartis import partis
```

Sedaj je potrebno ustvariti Partis sejo, ki jo bomo uporabljali za prenos vseh podatkov.
```python
partisScraper = partis.Partis("uporabnisko_ime", "geslo")
```

Če podatki za prijavo niso pravilni nam bo tolmač vrnil izjemo, sicer pa lahko nadaljujemo z uporabo funkcij Partisa.

## Iskanje torrentov
Za iskanje torrentov je potrebno poklicati funkcijo `iskanje`. Za primer glej spodaj.
```python
# Najdemo vse torrente s pomocjo kljucnih besed "Harry Potter"
torrenti = partisScraper.iskanje("Harry Potter")

# Za vsak torrent izpisemo njegov naslov
for torrent in torrenti:
	print(torrent.naslov)
```

Funkcijo `iskanje` je mogoče klicati z naslednjimi atributi (noben ni obvezen):
* `kljucne_besede` - ključne besede iskanja (te vpišemo v iskalno polje na vrhu strani)
* `stran` - zaporedna številka strani, ki jo želimo prenesti
* `kategorije` - seznam kategorij na Partis portalu
* `moznosti` - iskanje samo DrSI, freeleech ali MuSI torrentov
* `sortiranje` - po kakšnem ključu naj Partis sortira zadetke (vse možnosti so napisane spodaj)
  * `created_at` - Po datumu naraščajoče
  * `created_at desc` - Po datumu padajoče
  * `seeders` - Po sejalcih naraščajoče
  * `seeders desc` - Po sejalcih padajoče
  * `leechers` - Po pijavkah naraščajoče
  * `leechers desc` - Po pijavkah padajoče
  * `size` - Po velikosti naraščajoče
  * `size desc` - Po velikosti padajoče
  * `completed` - Po prenosih naraščajoče
  * `completed desc` - Po prenosih padajoče

Če funkcijo pokličemo brez parametrov, nam vrne seznam 20 zadnjih torrentov na partisu.

## Torrenti
Pri iskanju nam modul vrne seznam zadetkov. Vsak zadetek je objekt tipa `Torrent`.
Objekt ima naslednje funkcije:
* `oceni(ocena)` - ocenjevanje torrenta (najmanjsa ocena je 0, najvecja pa 5)
* `zahvaliSe()` - zahvali se za torrent
* `dodajMedZaznamke()` - dodajanje torrenta med zaznamke
* `odstraniIzZaznamkov()` - odstranjevanje torrenta iz zaznamkov
* `komentiraj(komentar)` - komentiranje torrenta (uporablja se lahko BB kodo)
* `prenesi(pot)` - prenos `*.torrent` datoteke s strežnika

Primer uporabe:
```python
# Najdemo 20 zadnjih torrentov
torrenti = partisScraper.iskanje()

# Iz seznama izberemo prvi torrent
zadnjiTorrent = torrenti[0]

# Pod torrent dodamo komentar
zadnjiTorrent.komentiraj("Super torrent, hvala nalagalcu")

# Torrentu damo 3 zvezdice
zadnjiTorrent.oceni(3)
```