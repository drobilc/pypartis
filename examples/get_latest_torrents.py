from pypartis import Partis

partis = Partis("spuzi_kvadratnik", "geslogeslo")

#Zadnje 3 torrente ocenimo s petimi zvezdicami
seznamTorrentov = partis.iskanje()

for torrent in seznamTorrentov[0:3]:
    torrent.oceni(5)

for torrent in seznamTorrentov[3:6]:
    torrent.odstraniIzZaznamkov()

for torrent in seznamTorrentov[6:9]:
    torrent.zahvaliSe()
