# 🗄️ Neon Database Integration für Zeltlager SUKU

## Übersicht

Die Streamlit App speichert jetzt alle Änderungen **automatisch in einer Neon PostgreSQL Datenbank**. Das bedeutet:

✅ **Keine Daten verloren** bei Refresh oder App-Neustart
✅ **Cloud-Backup** - Ihre Daten sind sicher gehostet
✅ **Multi-Session Support** - Mehrere Einkaufslisten gleichzeitig
✅ **Fallback zu lokal** - Wenn DB nicht verfügbar, wird lokal gespeichert

---

## 🚀 Schnell Setup (5 Minuten)

### 1. Neon Account erstellen (kostenlos!)

```
Gehen Sie zu: https://neon.tech/
Registrieren Sie sich (kostenlos)
Erstellen Sie ein neues Projekt
```

### 2. Connection String kopieren

```
Im Neon Dashboard:
1. Gehen Sie zu "Connection Details"
2. ⚠️ WICHTIG: Wählen Sie "Direct connection" (NICHT "Pooled connection")
3. Kopieren Sie die Connection String
4. Sie sollte so aussehen (OHNE "-pooler" im Hostname!):
   postgresql://user:password@ep-xyz.neon.tech/dbname?sslmode=require
```

**Häufiger Fehler:** "Pooled Connection" verwenden
- ❌ `postgresql://...@ep-xyz-pooler.neon.tech/...` (Falsch - hat "pooler" im Namen)
- ✅ `postgresql://...@ep-xyz.neon.tech/...` (Richtig - direkte Verbindung)

### 3. Secrets konfigurieren

**Option A: Lokal (zum Testen)**

Öffnen Sie `.streamlit/secrets.toml` im Projekt:

```toml
DATABASE_URL = "postgresql://user:password@host.neon.tech/dbname?sslmode=require"
```

**Option B: Streamlit Cloud (Production)**

https://docs.streamlit.io/develop/concepts/connections/secrets-management

1. Gehen Sie zu: https://share.streamlit.io/ (App-Dashboard)
2. Klicken Sie auf App-Menü → Secrets
3. Fügen Sie hinzu:

```toml
DATABASE_URL = "postgresql://user:password@host.neon.tech/dbname?sslmode=require"
```

### 4. Dependencies installieren

```powershell
pip install -r requirements-streamlit.txt
```

### 5. App starten

```powershell
streamlit run streamlit_app_advanced.py
```

---

## 🎯 Workflow

### Beim Einkaufen

1. **App öffnet** → Lädt automatisch Ihre letzten Änderungen aus Neon
2. **Sie einkaufen** → abhacken, verschieben, hinzufügen
3. **"💾 Änderungen speichern" klicken** → Speichert in Neon DB!
4. **App crasht?** → Beim nächsten Start alle Daten wieder da ✅

### Session-Verwaltung

In Tab "⚡ Einstellungen" → "🗄️ Datenbank Status" sehen Sie:
- ✅ Verbindungsstatus
- 📊 Anzahl gespeicherter Sessions  
- 📋 Liste aller Sessions
- 🗑️ Möglichkeit zum Löschen alter Sessions

---

## 📊 Was wird gespeichert?

In der Neon Datenbank werden folgende Tabellen angelegt:

### `shopping_sessions` Tabelle

| Spalte | Beschreibung |
|--------|-------------|
| `session_id` | Eindeutige Session-ID |
| `week_name` | Name der Woche/Wochentag |
| `checked_items` | JSON mit abhakemarken |
| `modified_items` | JSON mit verschobenen Artikeln |
| `new_items` | JSON mit neuen Artikeln |
| `created_at` | Erstellt um... |
| `updated_at` | Zuletzt aktualisiert um... |

**Beispiel JSON (wird direkt in DB gespeichert):**

```json
{
  "Aldi": {
    "Artikel1": true,
    "Artikel2": false
  },
  "Metro": { ... }
}
```

---

## ⚠️ Troubleshooting

### "connection to server ... failed: server closed the connection unexpectedly"

Dies ist der häufigste Fehler. **Ursache:** Sie verwenden die "Pooled Connection" statt "Direct Connection".

**Lösung:**
1. Öffnen Sie https://console.neon.tech/
2. Gehen Sie zu Ihrer Datenbank
3. Klicken Sie auf "Connection Details"
4. **WÄHLEN Sie "Direct connection"** (nicht "Pooled connection")
5. Kopieren Sie die NEUE Connection String (ohne "-pooler")
6. Bearbeiten `.streamlit/secrets.toml` und ersetzen Sie die alte URL
7. Starten Sie die App neu: `Ctrl+R` im Browser oder `Ctrl+C` & neu starten

**Kurzer Unterschied:**
```
Falsch (Pooled):       postgresql://...@ep-winter-dream-a9k8yxh9-pooler.gwc.azure.neon.tech/...
Richtig (Direct):     postgresql://...@ep-winter-dream-a9k8yxh9.gwc.azure.neon.tech/...
                      (kein "-pooler" im Namen!)
```

### "DATABASE_URL not set"

.streamlit/secrets.toml wurde nicht korrekt erstellt oder Streamlit hat es nicht geladen.

**Lösung:**
```toml
# .streamlit/secrets.toml - sieht so aus:
DATABASE_URL = "postgresql://user:password@host/db?sslmode=require"
```

Stellen Sie sicher:
- Datei heißt exakt `secrets.toml` (kleingeschrieben)
- Sie ist im `.streamlit/` Ordner
- Sie haben die Datei nach Edit gespeichert
- Starten Sie die App neu

### "invalid password" oder "authentication failed"

**Lösung:**
1. Überprüfen Sie Ihr Passwort in Neon Dashboard
2. Wenn das Passwort Sonderzeichen hat (`@`, `#`, `%`, etc.), kann es codiert werden müssen
3. Beispiel: `p@ssword` → `p%40ssword`
4. Oder nutzen Sie ein neues Passwort ohne Sonderzeichen

### Datenbank funktioniert, aber App lädt nicht

```
⚠️ Neon Datenbank nicht verbunden - nur lokale Speicherung aktiv
```

**Das ist OK!** Die App funktioniert auch ohne DB - nutzt dann lokal speicherung.
Ihre Daten gehen nicht verloren, werden nur lokal gespeichert.

---

## 🔒 Sicherheit

### Ihre Credentials sind sicher, weil:

✅ `DATABASE_URL` wird NICHT in Git committet (in `.gitignore`)
✅ Nur in `.streamlit/secrets.toml` lokal gespeichert
✅ Streamlit Cloud nutzt eige Secrets-Management
✅ Neon nutzt TLS/SSL Verschlüsselung

### Best Practices

1. **Niemals** DATABASE_URL in Code hardcoden
2. **Immer** `.streamlit/secrets.toml` in `.gitignore` haben
3. **Regelmäßig** alte Sessions löschen (über UI oder DB)
4. **Backup** - Neon macht automatische Backups (Pro-Plan)

---

## 📈 Skalierung

### Kostenlos mit Neon

- ✅ 1 CU-Hour pro Monat kostenlos
- ✅ Unbegrenzte Projekt-Branches
- ✅ Automatische Backups
- ✅ SSL Verschlüsselung

Das reicht locker für Ihr Zeltlager-Projekt!

---

## 🛠️ Erweiterte Konfiguration

### Manuelle Session löschen

```python
# In Python Console:
from src.neon_database import NeonDatabase
db = NeonDatabase("postgresql://...")
db.delete_session("session_id_hier")
```

### Alle Sessions exportieren

```python
sessions = db.list_sessions()
for sess in sessions:
    print(sess)
```

### Backup machen

Neon macht automatische Backups. Zusätzlich können Sie:

```powershell
# Mit pg_dump
pg_dump "postgresql://..." > backup.sql

# Mit CSV Export (aus Neon UI)
# Dashboard → Database → Export
```

---

## 📚 Ressourcen

- **Neon Docs**: https://neon.tech/docs
- **Streamlit Secrets**: https://docs.streamlit.io/develop/concepts/connections/secrets-management
- **SQLAlchemy**: https://docs.sqlalchemy.org/
- **PostgreSQL**: https://www.postgresql.org/docs/

---

## ✅ Checkliste vor dem Start

- [ ] Neon Account auf https://neon.tech/ erstellt
- [ ] Connection String kopiert (OHNE "-pooler"!)
- [ ] `.streamlit/secrets.toml` mit DATABASE_URL editiert
- [ ] `.streamlit/secrets.toml` gespeichert und geschlossen
- [ ] `pip install -r requirements-streamlit.txt` ausgeführt
- [ ] App gestartet: `streamlit run streamlit_app_advanced.py`
- [ ] Im Sidebar erscheint NICHT "❌ Datenbankverbindung fehlgeschlagen"
- [ ] Tab "⚡ Einstellungen" → "🗄️ Datenbank Status" zeigt "✅ verbunden"

**Falls Fehler:** Siehe Troubleshooting Sektion oben!

---

**Alles fertig? Viel Erfolg beim Einkaufen!** 🛒 🗄️
