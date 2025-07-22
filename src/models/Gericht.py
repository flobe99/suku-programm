
from models.Zutat import Zutat

class Gericht:
    zutat = []
    def __init__(self, mahlzeit:str, gerichtname:str, uhrzeit:str, zutat:Zutat):
        self.mahlzeit:str = mahlzeit
        self.gerichtname:str = gerichtname
        self.uhrzeit:str = uhrzeit
        self.zutat:Zutat = zutat
