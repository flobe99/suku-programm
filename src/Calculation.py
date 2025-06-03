import os

from Excel import Excel
from PDF import PDF

class Calculation:
    _excel = None
    
    def read_tage(self, workbooks):
        tage = []
        for workbook in workbooks:
            self._excel.read_page(workbook)
            tage.append(self._excel.read_tag())
        return tage
    
    def save_as_pdf(self, tage, target_folder):
        if not os.path.exists(target_folder):
            os.makedirs(target_folder)
        i=0 
        for tag in tage:
            _filename = f"{target_folder}/{i}_{tag.wochentag}.pdf"
            PDF.save_tag_as_table(tag, _filename)
            i+=1

    def run(self, file_base_path, filename, workbooks, output):
        self._excel = Excel()

        self._excel.read_file(filePath=os.path.join(file_base_path, filename))
        _tage = self.read_tage(workbooks)
        self.save_as_pdf(_tage, output)