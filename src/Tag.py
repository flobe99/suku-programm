from Gericht import Gericht
from People import People
class Tag:
    def __init__(self, people:People, datum:str, gericht:Gericht, wochentag:str):
        self.people:People = people
        self.datum:str = datum
        self.gericht:Gericht = gericht
        self.wochentag:str = wochentag
