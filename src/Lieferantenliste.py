import os
from typing import List

from Excel import Excel
from PDF import PDF
from Tag import Tag
from Laden import Laden

class Lieferantenliste:
    _excel = None
    
    def read_tage(self, workbooks) -> List[Tag]:
        tage = []
        for workbook in workbooks:
            self._excel.read_page(workbook)
            tage.append(self._excel.read_tag())
        return tage
    
    def save_as_pdf(self, einkaufsladen, target_folder):
        if not os.path.exists(target_folder):
            os.makedirs(target_folder)
        i=0 
        for laden in einkaufsladen:
            _filename = f"{target_folder}/{i}_{laden.Name}.pdf"
            PDF.save_zutaten_as_table(laden, _filename)
            i+=1

        PDF.save_in_one_file(target_folder, "Gesamt_Lieferanten.pdf")

    def create_lieferantenliste(self,tage, laden):
        zutaten = {}
        for tag in tage:
            for gerichte in tag.gericht:
                for zutat in gerichte.zutat:
                    if zutat.lieferant == laden:
                        key = (zutat.artikelname, zutat.einheit, zutat.kategorie, tag.wochentag)

                        if key not in zutaten:
                            zutaten[key] = {
                                "artikelname": zutat.artikelname,
                                "menge": float(zutat.menge),
                                "einheit": zutat.einheit,
                                "kategorie": zutat.kategorie,
                                "sonstiges": zutat.sonstiges,
                                "lieferant": zutat.lieferant,
                                "tag": tag.wochentag
                            }
                        else:
                            zutaten[key]["menge"] += float(zutat.menge)
                            # zutaten[key]["sonstiges"] += ", "+ zutat.sonstiges
                            zutaten[key]["tag"] += ", "+tag.wochentag
        return zutaten

    def run(self, file_base_path, filename, workbooks, lieferanten, output):
        self._excel = Excel()

        self._excel.read_file(filePath=os.path.join(file_base_path, filename))
        
        _tage = self.read_tage(workbooks)
        
        _lieferant:Laden = []
        for laden in lieferanten:
            zutaten = self.create_lieferantenliste(_tage, laden)
            zutaten = sorted(zutaten.values(), key=lambda z: z["kategorie"] or "")
            _lieferant.append(Laden(name=laden, zutaten=zutaten))

        self.save_as_pdf(_lieferant, target_folder=output)
