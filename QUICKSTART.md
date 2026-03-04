# ⚡ Streamlit Quick Start

## 3 Schritte zum Starten

### 1️⃣ PowerShell öffnen im Projektordner

```powershell
cd c:\Development\Sonstiges\suku-programm
```

### 2️⃣ Dependencies installieren (nur einmalig!)

```powershell
pip install -r requirements-streamlit.txt
```

### 3️⃣ App starten - Wählen Sie eine Version:

**OPTION A: Basis-Version (empfohlen für Anfänger)**
```powershell
streamlit run streamlit_app.py
```

**OPTION B: Advanced-Version (mit Interaktivität beim Einkaufen)**
```powershell
streamlit run streamlit_app_advanced.py
```

---

## 🎯 Was sich ändert

### Tkinter GUI → Streamlit
- ❌ Kein Desktop-Fenster mehr
- ✅ Öffnet sich im Browser (lokal: http://localhost:8501)
- ✅ Responsive Design (funktioniert auch auf Handy!)
- ✅ Einfacheres Filehandling (Upload statt "Durchsuchen")

---

## 🛒 Workflow beim Einkaufen (mit Advanced Version)

1. **App öffnen** → Excel hochladen
2. **In Tab "🛒 Einkaufsliste"** gehen
3. **Abhacken während Sie einkaufen**:
   - Artikel abhacken mit Checkbox ✅
   - Falls Artikel nicht im Shop: Mit Dropdown zu anderem Laden verschieben ➡️
   - Spontane Idee? ➕ Im unteren Bereich hinzufügen
4. **PDFs später downloaden** → Print oder mit zum nächsten Einkaufen

---

## 📊 Beide Versionen im Vergleich

<table>
  <tr>
    <th>Feature</th>
    <th>⚡ Basis</th>
    <th>🚀 Advanced</th>
  </tr>
  <tr>
    <td>Einkaufsliste ansehen</td>
    <td>✅</td>
    <td>✅</td>
  </tr>
  <tr>
    <td>Artikel abhacken</td>
    <td>❌</td>
    <td>✅</td>
  </tr>
  <tr>
    <td>Zwischen Läden verschieben</td>
    <td>❌</td>
    <td>✅ Auch zwischen Lieferanten!</td>
  </tr>
  <tr>
    <td>Spontan Artikel hinzufügen</td>
    <td>❌</td>
    <td>✅</td>
  </tr>
  <tr>
    <td>CSV Export</td>
    <td>❌</td>
    <td>✅</td>
  </tr>
  <tr>
    <td>Session verwenden/speichern</td>
    <td>❌</td>
    <td>✅ Mit JSON-Persistierung!</td>
  </tr>
  <tr>
    <td>Änderungen zwischen Sessions erhalten</td>
    <td>❌</td>
    <td>✅ Auto-Laden + Manuelles Speichern</td>
  </tr>
  <tr>
    <td>Dateigröße</td>
    <td>~3KB</td>
    <td>~20KB</td>
  </tr>
</table>

---

## 🚀 Tipps & Tricks

### Browser automatisch öffnen
Die App öffnet sich schon automatisch. Falls nicht:
```
http://localhost:8501
```

### Mehrere Fenster gleichzeitig
Wenn Sie Ihre Excel beim Einkaufen und Streamlit gleichzeitig nutzen wollen:
```powershell
# Terminal 1:
streamlit run streamlit_app_advanced.py

# Terminal 2 (oder neues PowerShell Fenster):
cd c:\Development\Sonstiges\suku-programm
# Excel öffnen
start Ihre_Datei.xlsx
```

### Schneller Wechsel zur Desktop-Version
Falls Sie doch lieber bei der Tkinter GUI bleiben:
```powershell
python src/main.py
```

### Port ändern (falls 8501 belegt)
```powershell
streamlit run streamlit_app_advanced.py --server.port 8502
```

---

## 💾 Persistierung & Speichern (Advanced Version)

### Automatisches Laden beim Start
Ihre Änderungen werden automatisch geladen, wenn Sie die App neu starten:
- ✅ Abhakemarken bleiben erhalten
- ✅ Verschobene Artikel bleiben an ihrem neuen Ort
- ✅ Neue Artikel, die Sie hinzugefügt haben, sind noch da

**Speicherort:** `%USERPROFILE%\.suku_planung\einkaufslisten_changes.json`

### Manuell Speichern (empfohlen nach Einkauf)
1. Gehen Sie zu Tab "⚡ Einstellungen"
2. Klicken Sie auf "💾 Änderungen speichern"
3. Status zeigt die Uhrzeit der letzten Speicherung

### Änderungen Exportieren/Importieren
**Exportieren** (mit anderen teilen oder archivieren):
- Tab "⚡ Einstellungen"
- Button "📤 Änderungen exportieren (JSON)"
- JSON-Datei wird heruntergeladen

**Importieren** (von gespeicherten Änderungen):
- Tab "⚡ Einstellungen"
- Upload-Button "📥 Änderungen importieren (JSON)"
- Wählen Sie eine vorher exportierte JSON-Datei
- Änderungen werden geladen!

### Szenario: Einkauf unterbrechen & fortsetzen
1. **Einkauf starten:** App laden → Excel hochladen → einkaufen anfangen
2. **Unterbruch:** Abhacken "💾 Änderungen speichern" → App schließen
3. **Später fortsetzen:** App erneut starten → Excel laden → Ihre Änderungen sind da! ✅

---

## 🛠️ Troubleshooting

**"ModuleNotFoundError"?**
```powershell
pip install -r requirements-streamlit.txt --force-reinstall
```

**"Port 8501 is already in use"?**
- Alte Streamlit-Prozesse killen:
```powershell
Get-Process python | Where-Object {$_.CommandLine -like "*streamlit*"} | Stop-Process -Force
```

**App sehr langsam?**
- Cache leeren: Ctrl+F5 im Browser
- Oder neuen Port nutzen: `streamlit run streamlit_app_advanced.py --server.port 8502`

---

## 💡 Nächste Schritte (Optional)

1. **PDF-Generierung beschleunigen**: Caching einbauen
2. ✅ **Persistente Speicherung**: JSON-Dateien speichern statt nur Session-State (BEREITS IMPLEMENTIERT!)
3. **Multiuser**: Mit Streamlit Cloud deployen (kostenlos!)
4. **Mobile Optimierung**: Responsives Design verfeinern

---

## ❓ FAQ

**F: Warum ist die App schneller zu entwickeln als die Tkinter GUI?**
A: Streamlit abstrahiert viele UI-Tasks automatisch. Keine komplexen Layout-Manager nötig.

**F: Kann ich die App auch auf meinem Handy nutzen?**
A: Ja, wenn Sie einen kleinen Server daneben laufen lassen. Vorerst: Lokal am Laptop.

**F: Werden meine Änderungen beim Einkaufen gespeichert?**
A: Ja! Automatisch im Speicherordner. Mit "💾 Änderungen speichern" auch manuell verfügbar. Nach `Ctrl+C` oder Browser-Refresh gehen sie NICHT verloren - beim nächsten App-Start sind sie automatisch da! ✅

**F: Wo werden meine Daten gespeichert?**
A: In `%USERPROFILE%\.suku_planung\einkaufslisten_changes.json` (Ihr Windows Home-Verzeichnis)

**F: Kann ich Änderungen mit anderen teilen?**
A: Ja! Button "📤 Änderungen exportieren (JSON)" und danach versenden oder auf USB-Stick kopieren. Andere können diese dann mit "📥 Änderungen importieren" laden.

**F: Kann ich beides (Tkinter + Streamlit) gleichzeitig nutzen?**
A: Sicher! Tkinter und Streamlit sind unabhängig.

---

Debugging via `streamlit run streamlit_app_advanced.py --logger.level=debug`
