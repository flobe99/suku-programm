from Lieferant import Lieferant
from Kategorie import Kategorie
from Einheit import Einheit

class Zutat:
    def __init__(self, lieferant:Lieferant, kategorie:Kategorie, menge:Einheit, einheit:str, artikelname:str, faktor:float, sonstiges:str):
        self.lieferant = lieferant
        self.kategorie = kategorie
        self.menge = menge
        self.einheit = einheit
        self.artikelname = artikelname
        self.faktor = faktor
        self.sonstiges = sonstiges
