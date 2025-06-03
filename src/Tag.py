from Gericht import Gericht

class Tag:
    def __init__(self, datum:str, gericht:Gericht, wochentag:str):
        self.datum:str = datum
        self.gericht:Gericht = gericht
        self.wochentag:str = wochentag
