import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk

from Calculation import Calculation
from Einkaufsliste import Einkaufsliste
from config import workbooks_default, laden_default, lieferanten_default

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Wochenplaner Tool")

        # Werte
        self.mode = tk.StringVar(value="calculation")
        self.filename = tk.StringVar()
        self.base_path = tk.StringVar()
        self.workbooks = tk.StringVar()
        self.output_path = tk.StringVar()
        self.läden = tk.StringVar()

        # UI-Elemente
        self.create_widgets()

    def create_widgets(self):
        # Modus Auswahl
        ttk.Label(self.root, text="Modus:").grid(row=0, column=0, sticky="w")
        ttk.OptionMenu(self.root, self.mode, "calculation", "calculation", "einkaufsliste", "lieferantenliste").grid(row=0, column=1, sticky="ew")

        # Datei auswählen
        ttk.Label(self.root, text="Excel-Datei:").grid(row=1, column=0, sticky="w")
        ttk.Entry(self.root, textvariable=self.filename, width=60).grid(row=1, column=1, sticky="ew")
        ttk.Button(self.root, text="Durchsuchen", command=self.browse_file).grid(row=1, column=2)

        # Basis-Pfad
        ttk.Label(self.root, text="Basis-Pfad:").grid(row=2, column=0, sticky="w")
        ttk.Entry(self.root, textvariable=self.base_path, width=60).grid(row=2, column=1, sticky="ew")
        ttk.Button(self.root, text="Durchsuchen", command=self.browse_folder).grid(row=2, column=2)

        # Workbooks
        self.workbooks = tk.StringVar(value=", ".join(workbooks_default))
        ttk.Label(self.root, text="Excel Blätter (kommagetrennt):").grid(row=3, column=0, sticky="w")
        ttk.Entry(self.root, textvariable=self.workbooks).grid(row=3, column=1, sticky="ew")

        # Ausgabepfad
        ttk.Label(self.root, text="Ausgabeordner:").grid(row=4, column=0, sticky="w")
        ttk.Entry(self.root, textvariable=self.output_path).grid(row=4, column=1, sticky="ew")
        ttk.Button(self.root, text="Durchsuchen", command=self.browse_output_folder).grid(row=4, column=2)

        # Läden/Lieferanten
        self.läden = tk.StringVar(value=", ".join(laden_default))
        ttk.Label(self.root, text="Laden/Lieferanten (kommagetrennt):").grid(row=5, column=0, sticky="w")
        ttk.Entry(self.root, textvariable=self.läden).grid(row=5, column=1, sticky="ew")

        # Start Button
        ttk.Button(self.root, text="Start", command=self.run_tool).grid(row=6, column=0, columnspan=3, pady=10)

    def browse_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx *.xlsm *.xls")])
        if file_path:
            self.filename.set(file_path)
            self.base_path.set(os.path.dirname(file_path))

    def browse_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.base_path.set(folder)

    def browse_output_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.output_path.set(folder)

    def run_tool(self):
        try:
            mode = self.mode.get()
            filename = os.path.basename(self.filename.get())
            base_path = self.base_path.get()
            workbooks = [w.strip() for w in self.workbooks.get().split(",") if w.strip()]
            output = self.output_path.get()
            läden = [l.strip() for l in self.läden.get().split(",") if l.strip()]

            if mode == "calculation":
                _calc = Calculation()
                _calc.run(file_base_path=base_path, filename=filename, workbooks=workbooks, output=output)
            elif mode in ("einkaufsliste", "lieferantenliste"):
                _einkaufsliste = Einkaufsliste()
                _einkaufsliste.run(file_base_path=base_path, filename=filename, workbooks=workbooks, output=output, läden=läden)
            else:
                messagebox.showerror("Fehler", f"Unbekannter Modus: {mode}")
                return

            messagebox.showinfo("Fertig", "Verarbeitung abgeschlossen.")
        except Exception as e:
            messagebox.showerror("Fehler", str(e))


if __name__ == "__main__":
    import os
    root = tk.Tk()
    root.geometry("700x300")
    app = App(root)
    root.mainloop()
