import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
from PIL import Image, ImageTk

from Calculation import Calculation
from Einkaufsliste import Einkaufsliste
from Lieferantenliste import Lieferantenliste
from config import workbooks_default, laden_default, lieferanten_default
import os
from pathlib import Path

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Zeltlager SUKU")

        self.mode = tk.StringVar(value="calculation")
        self.filename = tk.StringVar()
        self.base_path = tk.StringVar()
        self.workbooks = tk.StringVar()
        self.output_path = tk.StringVar()
        self.läden = tk.StringVar()
        self.lieferanten = tk.StringVar()

        self.create_widgets()

    def create_widgets(self):
        ttk.Label(self.root, text="Modus:").grid(row=0, column=0, sticky="w")

        ttk.OptionMenu(
            self.root,
            self.mode,
            "calculation",
            "calculation", "einkaufsliste", "lieferantenliste",
            command=lambda *_: self._set_output_default_if_empty()
        ).grid(row=0, column=1, sticky="ew")


        ttk.Label(self.root, text="Excel-Datei:").grid(row=1, column=0, sticky="w")
        ttk.Entry(self.root, textvariable=self.filename, width=60).grid(row=1, column=1, sticky="ew")
        ttk.Button(self.root, text="Durchsuchen", command=self.browse_file).grid(row=1, column=2)

        self.workbooks = tk.StringVar(value=", ".join(workbooks_default))
        ttk.Label(self.root, text="Excel Blätter (kommagetrennt):").grid(row=3, column=0, sticky="w")
        ttk.Entry(self.root, textvariable=self.workbooks).grid(row=3, column=1, sticky="ew")

        ttk.Label(self.root, text="Ausgabeordner:").grid(row=4, column=0, sticky="w")
        ttk.Entry(self.root, textvariable=self.output_path).grid(row=4, column=1, sticky="ew")
        ttk.Button(self.root, text="Durchsuchen", command=self.browse_output_folder).grid(row=4, column=2)

        self.läden = tk.StringVar(value=", ".join(laden_default))
        ttk.Label(self.root, text="Laden (kommagetrennt):").grid(row=5, column=0, sticky="w")
        ttk.Entry(self.root, textvariable=self.läden).grid(row=5, column=1, sticky="ew")

        self.lieferanten = tk.StringVar(value=", ".join(lieferanten_default))
        ttk.Label(self.root, text="Lieferanten (kommagetrennt):").grid(row=6, column=0, sticky="w")
        ttk.Entry(self.root, textvariable=self.lieferanten).grid(row=6, column=1, sticky="ew")

        ttk.Button(self.root, text="Start", command=self.run_tool).grid(row=7, column=0, columnspan=3, pady=10)

    def browse_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx *.xlsm *.xls")])
        if file_path:
            self.filename.set(file_path)
            self.base_path.set(os.path.dirname(file_path))
            self._set_output_default_if_empty()

    def browse_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.base_path.set(folder)
            self._set_output_default_if_empty()

    def browse_output_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.output_path.set(folder)

    def _compute_default_output(self) -> Path:
        base = Path(self.base_path.get().strip() or ".")
        mode = (self.mode.get() or "calculation").strip()
        return base / "build" / mode

    def _set_output_default_if_empty(self):
        if not self.output_path.get().strip():
            self.output_path.set(str(self._compute_default_output()))

    def run_tool(self):
        try:
            mode = (self.mode.get() or "").strip()
            if mode not in {"calculation", "einkaufsliste", "lieferantenliste"}:
                messagebox.showerror("Fehler", f"Unbekannter Modus: {mode or '<leer>'}")
                return

            filename_full = (self.filename.get() or "").strip()
            if not filename_full:
                messagebox.showerror("Fehler", "Bitte eine Excel-Datei auswählen.")
                return

            base_path_str = (self.base_path.get() or "").strip()
            if not base_path_str:
                base_path_str = os.path.dirname(filename_full)
                self.base_path.set(base_path_str)

            base_path = Path(base_path_str)
            if not base_path.exists():
                messagebox.showerror("Fehler", f"Basisordner existiert nicht:\n{base_path}")
                return

            filename = os.path.basename(filename_full)

            workbooks = [w.strip() for w in (self.workbooks.get() or "").split(",") if w.strip()]
            laeden = [l.strip() for l in (self.läden.get() or "").split(",") if l.strip()]
            lieferanten = [l.strip() for l in (self.lieferanten.get() or "").split(",") if l.strip()]

            output_raw = (self.output_path.get() or "").strip()
            if not output_raw:
                output_path = self._compute_default_output()
            else:
                output_path = Path(output_raw)

            output_path.mkdir(parents=True, exist_ok=True)

            if mode == "calculation":
                _calc = Calculation()
                _calc.run(
                    file_base_path=str(base_path),
                    filename=filename,
                    workbooks=workbooks,
                    output=str(output_path)
                )
            elif mode == "einkaufsliste":
                _einkaufsliste = Einkaufsliste()
                _einkaufsliste.run(
                    file_base_path=str(base_path),
                    filename=filename,
                    workbooks=workbooks,
                    output=str(output_path),
                    läden=laeden
                )
            elif mode == "lieferantenliste":
                _lieferantenliste = Lieferantenliste()
                _lieferantenliste.run(
                    file_base_path=str(base_path),
                    filename=filename,
                    workbooks=workbooks,
                    output=str(output_path),
                    lieferanten=lieferanten
                )
            else:
                messagebox.showerror("Fehler", f"Unbekannter Modus: {mode}")
                return

            messagebox.showinfo("Fertig", f"Verarbeitung abgeschlossen.\nAusgabeordner:\n{output_path}")

        except Exception as e:
            messagebox.showerror("Fehler", str(e))

if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("700x300")
    
# Icon setzen
    try:
        icon_image = Image.open("../img/logo_smj_ulm.jpg")
        icon_photo = ImageTk.PhotoImage(icon_image)
        root.iconphoto(False, icon_photo)
    except Exception as e:
        print(f"Fehler beim Laden des Icons: {e}")

    app = App(root)
    root.mainloop()
