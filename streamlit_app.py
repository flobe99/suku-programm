import streamlit as st
import os
import tempfile
from pathlib import Path
import pandas as pd
from io import BytesIO

# Workspace relative imports
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.Calculation import Calculation
from src.Einkaufsliste import Einkaufsliste
from src.Lieferantenliste import Lieferantenliste
from src.Excel import Excel
from src.config import workbooks_default, laden_default, lieferanten_default

# Streamlit Page Configuration
st.set_page_config(page_title="Zeltlager SUKU Planung", layout="wide", initial_sidebar_state="expanded")
st.title("🍽️ Zeltlager SUKU - Essensplanung")

# Initialize session state
if "tage" not in st.session_state:
    st.session_state.tage = None
if "einkaufsladen" not in st.session_state:
    st.session_state.einkaufsladen = None
if "einkaufslisten_dict" not in st.session_state:
    st.session_state.einkaufslisten_dict = {}
if "modifications" not in st.session_state:
    st.session_state.modifications = {}

# ============= SIDEBAR KONFIGURATION =============
st.sidebar.header("⚙️ Konfiguration")

uploaded_file = st.sidebar.file_uploader("📊 Excel-Datei hochladen", type=["xlsx", "xls"])

workbooks = st.sidebar.text_input(
    "Excel Blätter (kommagetrennt):",
    value=", ".join(workbooks_default)
)
workbooks_list = [wb.strip() for wb in workbooks.split(",")]

läden = st.sidebar.text_input(
    "Läden (kommagetrennt):",
    value=", ".join(laden_default)
)
läden_list = [l.strip() for l in läden.split(",")]

lieferanten = st.sidebar.text_input(
    "Lieferanten (kommagetrennt):",
    value=", ".join(lieferanten_default)
)
lieferanten_list = [lf.strip() for lf in lieferanten.split(",")]

# ============= DATEI VERARBEITUNG =============
if uploaded_file is not None:
    with tempfile.TemporaryDirectory() as tmpdir:
        file_path = os.path.join(tmpdir, uploaded_file.name)
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        # Laden der Daten
        try:
            excel = Excel()
            excel.read_file(file_path)
            
            # Tage aus Workbooks laden
            tage = []
            for workbook in workbooks_list:
                excel.read_page(workbook)
                tag = excel.read_tag()
                tage.append(tag)
            st.session_state.tage = tage
            
            # Einkaufslisten nach Läden erstellen
            einkaufsliste = Einkaufsliste()
            einkaufslisten_dict = {}
            for laden in läden_list:
                einkaufslisten_dict[laden] = einkaufsliste.create_einkaufsliste(tage, laden)
            st.session_state.einkaufslisten_dict = einkaufslisten_dict
            
            st.sidebar.success("✅ Datei erfolgreich verarbeitet!")
            
        except Exception as e:
            st.sidebar.error(f"❌ Fehler beim Verarbeiten: {str(e)}")

# ============= HAUPTINHALT =============
if st.session_state.tage is None:
    st.info("📁 Bitte laden Sie zuerst eine Excel-Datei hoch (siehe Sidebar)")
else:
    # Tabs für verschiedene Ansichten
    tab1, tab2, tab3, tab4 = st.tabs([
        "🛒 Einkaufsliste",
        "📊 Kalkulation",
        "🚚 Lieferanten",
        "📥 Download"
    ])
    
    # ============= TAB 1: EINKAUFSLISTE =============
    with tab1:
        st.header("Einkaufsliste nach Läden")
        
        if st.session_state.einkaufslisten_dict:
            # Läden in Spalten anzeigen
            cols = st.columns(len(läden_list))
            
            for col_idx, laden in enumerate(läden_list):
                with cols[col_idx]:
                    st.subheader(f"🏪 {laden}")
                    
                    zutaten_list = st.session_state.einkaufslisten_dict.get(laden, {})
                    
                    if zutaten_list:
                        # DataFrame für bessere Darstellung
                        df_data = []
                        for (artikelname, menge, einheit, kategorie, sonstiges, lieferant, tag), zutat_info in zutaten_list.items():
                            df_data.append({
                                "Artikel": zutat_info["artikelname"],
                                "Menge": zutat_info["menge"],
                                "Einheit": zutat_info["einheit"],
                                "Kategorie": zutat_info["kategorie"],
                                "Tag": zutat_info["tag"],
                                "✓": False  # Checkbox zum Abhacken
                            })
                        
                        df = pd.DataFrame(df_data)
                        edited_df = st.data_editor(
                            df,
                            use_container_width=True,
                            hide_index=True,
                            key=f"editor_{laden}"
                        )
                        
                        st.caption(f"📋 {len(df_data)} Artikel")
                    else:
                        st.info("Keine Artikel für diesen Laden")
        else:
            st.warning("Keine Einkaufslisten verfügbar")
    
    # ============= TAB 2: KALKULATION =============
    with tab2:
        st.header("Essensplanung nach Wochentag")
        
        if st.session_state.tage:
            for tag in st.session_state.tage:
                with st.expander(f"📅 {tag.wochentag}"):
                    for gericht in tag.gericht:
                        st.subheader(f"🍴 {gericht.gerichtname}")
                        
                        # Zutaten als Tabelle
                        zutat_data = []
                        for zutat in gericht.zutat:
                            zutat_data.append({
                                "Artikel": zutat.artikelname,
                                "Menge": zutat.menge,
                                "Einheit": zutat.einheit,
                                "Laden": zutat.lieferant,
                                "Kategorie": zutat.kategorie
                            })
                        
                        if zutat_data:
                            st.dataframe(zutat_data, use_container_width=True, hide_index=True)
                        else:
                            st.info("Keine Zutaten")
    
    # ============= TAB 3: LIEFERANTEN =============
    with tab3:
        st.header("Übersicht Lieferanten")
        
        if st.session_state.tage:
            lieferantenliste = Lieferantenliste()
            try:
                lieferanten_dict = lieferantenliste.create_lieferantenliste(
                    st.session_state.tage,
                    lieferanten_list
                )
                
                lieferanten_cols = st.columns(len(lieferanten_list))
                for col_idx, lieferant_name in enumerate(lieferanten_list):
                    with lieferanten_cols[col_idx]:
                        st.subheader(f"🚚 {lieferant_name}")
                        
                        zutaten_list = lieferanten_dict.get(lieferant_name, {})
                        if zutaten_list:
                            lieferant_data = []
                            for zutat_info in zutaten_list.values():
                                lieferant_data.append({
                                    "Artikel": zutat_info["artikelname"],
                                    "Menge": zutat_info["menge"],
                                    "Einheit": zutat_info["einheit"]
                                })
                            
                            st.dataframe(lieferant_data, use_container_width=True, hide_index=True)
                        else:
                            st.info("Keine Artikel")
            except Exception as e:
                st.warning(f"Lieferantenliste konnte nicht erstellt werden: {str(e)}")
    
    # ============= TAB 4: DOWNLOAD =============
    with tab4:
        st.header("📥 PDF Download")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("📊 Kalkulation als PDF"):
                with tempfile.TemporaryDirectory() as tmpdir:
                    try:
                        calculation = Calculation()
                        calculation.save_as_pdf(st.session_state.tage, tmpdir)
                        
                        # Zusammenfassung lesen
                        pdf_path = os.path.join(tmpdir, "Gesamt_Calc.pdf")
                        if os.path.exists(pdf_path):
                            with open(pdf_path, "rb") as pdf_file:
                                st.download_button(
                                    label="⬇️ Herunterladen (Kalkulation)",
                                    data=pdf_file.read(),
                                    file_name="Gesamt_Kalkulation.pdf",
                                    mime="application/pdf"
                                )
                            st.success("✅ Kalkulation PDF erstellt!")
                    except Exception as e:
                        st.error(f"Fehler: {str(e)}")
        
        with col2:
            if st.button("🛒 Einkaufsliste als PDF"):
                with tempfile.TemporaryDirectory() as tmpdir:
                    try:
                        # Hier benötigen Sie die Laden-Objekte
                        # Das ist abhängig von Ihrer Einkaufsliste Implementierung
                        st.info("Feature wird in Kürze implementiert")
                    except Exception as e:
                        st.error(f"Fehler: {str(e)}")
        
        with col3:
            if st.button("🚚 Lieferanten als PDF"):
                with tempfile.TemporaryDirectory() as tmpdir:
                    try:
                        lieferantenliste = Lieferantenliste()
                        lieferantenliste.save_as_pdf(st.session_state.tage, lieferanten_list, tmpdir)
                        
                        pdf_path = os.path.join(tmpdir, "Gesamt_Lieferanten.pdf")
                        if os.path.exists(pdf_path):
                            with open(pdf_path, "rb") as pdf_file:
                                st.download_button(
                                    label="⬇️ Herunterladen (Lieferanten)",
                                    data=pdf_file.read(),
                                    file_name="Gesamt_Lieferanten.pdf",
                                    mime="application/pdf"
                                )
                            st.success("✅ Lieferanten PDF erstellt!")
                    except Exception as e:
                        st.error(f"Fehler: {str(e)}")

# ============= FOOTER =============
st.divider()
st.caption("🧑‍💻 Zeltlager SUKU Essensplanung | Streamlit Version")
