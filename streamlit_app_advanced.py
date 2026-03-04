"""
ERWEITERTE STREAMLIT VERSION mit Laden-Management
Ermöglicht Verschieben von Artikeln zwischen Läden beim Einkaufen
"""

import streamlit as st
import os
import tempfile
import json
from pathlib import Path
from datetime import datetime
import pandas as pd
from io import BytesIO
import pickle

# Workspace relative imports
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.Calculation import Calculation
from src.Einkaufsliste import Einkaufsliste
from src.Lieferantenliste import Lieferantenliste
from src.Excel import Excel
from src.config import workbooks_default, laden_default, lieferanten_default
from src.models.Laden import Laden

# Streamlit Page Configuration
st.set_page_config(
    page_title="Zeltlager SUKU Planung ADVANCED",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'About': "🍽️ Zeltlager SUKU Essensplanung mit Streamlit"
    }
)

# Custom CSS für besseres Design
st.markdown("""
<style>
    .einkaufsliste-item {
        padding: 10px;
        margin: 5px 0;
        border-radius: 5px;
        background-color: #f0f0f0;
    }
    .checked-item {
        text-decoration: line-through;
        opacity: 0.6;
    }
</style>
""", unsafe_allow_html=True)

st.title("🍽️ Zeltlager SUKU - Essensplanung ADVANCED")

# Initialize session state
if "tage" not in st.session_state:
    st.session_state.tage = None
if "einkaufslisten_dict" not in st.session_state:
    st.session_state.einkaufslisten_dict = {}
if "artikel_modifikationen" not in st.session_state:
    st.session_state.artikel_modifikationen = {}  # {artikel_key: neuer_laden}
if "neue_artikel" not in st.session_state:
    st.session_state.neue_artikel = []
if "abgehakte_artikel" not in st.session_state:
    st.session_state.abgehakte_artikel = {}  # {laden: [artikel_keys]}

# ============= SIDEBAR KONFIGURATION =============
with st.sidebar:
    st.sidebar.header("⚙️ Konfiguration")
    
    uploaded_file = st.file_uploader("📊 Excel-Datei hochladen", type=["xlsx", "xls", "xlsm"], key="excel_upload")
    
    workbooks = st.text_input(
        "Excel Blätter (kommagetrennt):",
        value=", ".join(workbooks_default)
    )
    workbooks_list = [wb.strip() for wb in workbooks.split(",")]
    
    läden = st.text_input(
        "Läden (kommagetrennt):",
        value=", ".join(laden_default)
    )
    läden_list = [l.strip() for l in läden.split(",")]
    
    lieferanten = st.text_input(
        "Lieferanten (kommagetrennt):",
        value=", ".join(lieferanten_default)
    )
    lieferanten_list = [lf.strip() for lf in lieferanten.split(",")]
    
    st.divider()
    st.header("📊 Session Info")
    if st.session_state.tage:
        st.success(f"✅ {len(st.session_state.tage)} Wochentage geladen")
        st.metric("Shops", len(läden_list))
        
        # Statistiken
        gesamt_artikel = sum(len(items) for items in st.session_state.einkaufslisten_dict.values())
        st.metric("Artikel gesamt", gesamt_artikel)

# ============= DATEI VERARBEITUNG =============
if uploaded_file is not None:
    with tempfile.TemporaryDirectory() as tmpdir:
        file_path = os.path.join(tmpdir, uploaded_file.name)
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
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
            st.sidebar.write(str(e))

# ============= HAUPTINHALT =============
if st.session_state.tage is None:
    st.info("📁 Bitte laden Sie zuerst eine Excel-Datei hoch (siehe Sidebar)")
else:
    # Tabs für verschiedene Ansichten
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🛒 Einkaufsliste (INTERAKTIV)",
        "📊 Kalkulation",
        "🚚 Lieferanten",
        "📥 Download",
        "⚡ Einstellungen"
    ])
    
    # ============= TAB 1: EINKAUFSLISTE MIT INTERAKTIVITÄT =============
    with tab1:
        st.header("🛒 Einkaufsliste - INTERAKTIVER MODUS")
        st.write("""
        💡 **Tipps zum Einkaufen**:
        - ✅ Artikel abhacken, während Sie einkaufen
        - 🔄 Artikel zu anderem Laden verschieben (wenn nicht verfügbar)
        - ➕ Neue spontane Ideen hinzufügen
        """)
        
        if st.session_state.einkaufslisten_dict:
            col_info = st.columns([2, 1, 1])
            
            with col_info[1]:
                view_mode = st.radio("Ansicht:", ["🏪 Nach Läden", "✅ Abhaken"])
            
            # MODUS 1: Nach Läden sortiert
            if view_mode == "🏪 Nach Läden":
                cols = st.columns(min(3, len(läden_list)))  # Max 3 Spalten
                
                for col_idx, laden in enumerate(läden_list):
                    with cols[col_idx % 3]:
                        st.subheader(f"🏪 {laden}")
                        
                        zutaten_list = st.session_state.einkaufslisten_dict.get(laden, {})
                        
                        if zutaten_list:
                            st.write(f"📋 **{len(zutaten_list)} Artikel**")
                            
                            # Artikel mit Umzugs-Option
                            for zutat_key, zutat_info in zutaten_list.items():
                                col_artikel, col_umzug = st.columns([3, 1])
                                
                                with col_artikel:
                                    checkbox_key = f"check_{laden}_{zutat_key}"
                                    is_checked = st.checkbox(
                                        f"**{zutat_info['artikelname']}** "
                                        f"({zutat_info['menge']} {zutat_info['einheit']})",
                                        key=checkbox_key,
                                        value=st.session_state.abgehakte_artikel.get(laden, {}).get(str(zutat_key), False)
                                    )
                                    
                                    # Update abgehakte Artikel
                                    if laden not in st.session_state.abgehakte_artikel:
                                        st.session_state.abgehakte_artikel[laden] = {}
                                    st.session_state.abgehakte_artikel[laden][str(zutat_key)] = is_checked
                                
                                with col_umzug:
                                    if st.selectbox(
                                        "➡️",
                                        ["Hierbleiben"] + [l for l in läden_list if l != laden],
                                        key=f"move_{laden}_{zutat_key}"
                                    ) != "Hierbleiben":
                                        st.info(f"✅ {zutat_info['artikelname']} markiert zum Verschieben")
                        else:
                            st.info("Keine Artikel für diesen Laden")
            
            # MODUS 2: Nach Kategorien mit Abhaken
            else:
                st.subheader("✅ Einkaufen - Abhaken im Fortschritt")
                
                all_artikel_by_category = {}
                for laden, zutaten in st.session_state.einkaufslisten_dict.items():
                    for zutat_info in zutaten.values():
                        cat = zutat_info.get("kategorie") or "Sonstiges"
                        if cat not in all_artikel_by_category:
                            all_artikel_by_category[cat] = []
                        all_artikel_by_category[cat].append({
                            "name": zutat_info["artikelname"],
                            "menge": zutat_info["menge"],
                            "einheit": zutat_info["einheit"],
                            "laden": laden,
                            "tag": zutat_info["tag"]
                        })
                
                for kategorie in sorted(all_artikel_by_category.keys(), key=lambda x: (x is None, x)):
                    with st.expander(f"🏷️ {kategorie}"):
                        for idx, artikel in enumerate(all_artikel_by_category[kategorie]):
                            col1, col2, col3 = st.columns([2, 1, 1])
                            
                            with col1:
                                st.checkbox(
                                    f"{artikel['name']} ({artikel['menge']} {artikel['einheit']})",
                                    key=f"cat_{kategorie}_{artikel['laden']}_{idx}"
                                )
                            
                            with col2:
                                st.caption(f"🏪 {artikel['laden']}")
                            
                            with col3:
                                st.caption(f"📅 {artikel['tag']}")
            
            # NEUER ARTIKEL hinzufügen
            st.divider()
            st.subheader("➕ Spontane Idee? Neuen Artikel hinzufügen")
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                new_artikel = st.text_input("Artikel Name:", placeholder="z.B. Papierservietten")
            
            with col2:
                new_menge = st.number_input("Menge:", min_value=0.0, step=0.5, value=1.0)
            
            with col3:
                new_einheit = st.selectbox("Einheit:", ["kg", "Stk", "L", "ml", "Pack", "Becher", "Dose"])
            
            with col4:
                new_laden = st.selectbox("Laden:", läden_list)
            
            if st.button("➕ Artikel hinzufügen", use_container_width=True):
                if new_artikel:
                    new_key = (new_artikel, new_einheit, "Spontan")
                    st.session_state.einkaufslisten_dict[new_laden][new_key] = {
                        "artikelname": new_artikel,
                        "menge": new_menge,
                        "einheit": new_einheit,
                        "kategorie": "Spontan",
                        "sonstiges": "Spontan hinzugefügt",
                        "lieferant": new_laden,
                        "tag": "Einkauf"
                    }
                    st.success(f"✅ '{new_artikel}' zu {new_laden} hinzugefügt!")
                    st.rerun()
                else:
                    st.warning("Bitte Artikelname eingeben!")
        else:
            st.warning("Keine Einkaufslisten verfügbar")
    
    # ============= TAB 2: KALKULATION =============
    with tab2:
        st.header("📊 Essensplanung nach Wochentag")
        
        if st.session_state.tage:
            for tag in st.session_state.tage:
                with st.expander(f"📅 {tag.wochentag}", expanded=False):
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
        st.header("🚚 Übersicht Lieferanten")
        
        if st.session_state.tage:
            lieferantenliste = Lieferantenliste()
            try:
                for lieferant_name in lieferanten_list:
                    lieferanten_dict_temp = lieferantenliste.create_lieferantenliste(
                        st.session_state.tage,
                        lieferant_name
                    )
                    
                    with st.expander(f"🚚 {lieferant_name}", expanded=False):
                        if lieferanten_dict_temp:
                            lieferant_data = []
                            for zutat_info in lieferanten_dict_temp.values():
                                lieferant_data.append({
                                    "Artikel": zutat_info["artikelname"],
                                    "Menge": zutat_info.get("menge", 0),
                                    "Einheit": zutat_info.get("einheit", ""),
                                    "Kategorie": zutat_info.get("kategorie", "")
                                })
                            
                            st.dataframe(lieferant_data, use_container_width=True, hide_index=True)
                        else:
                            st.info("Keine Artikel")
            except Exception as e:
                st.warning(f"Fehler: {str(e)}")
    
    # ============= TAB 4: DOWNLOAD =============
    with tab4:
        st.header("📥 PDF Download & Export")
        
        col1, col2, col3 = st.columns(3)
        
        # Kalkulation PDF
        with col1:
            if st.button("📊 Kalkulation als PDF", use_container_width=True):
                with tempfile.TemporaryDirectory() as tmpdir:
                    try:
                        calculation = Calculation()
                        calculation.save_as_pdf(st.session_state.tage, tmpdir)
                        
                        pdf_path = os.path.join(tmpdir, "Gesamt_Calc.pdf")
                        if os.path.exists(pdf_path):
                            with open(pdf_path, "rb") as pdf_file:
                                st.download_button(
                                    label="⬇️ Herunterladen",
                                    data=pdf_file.read(),
                                    file_name=f"Kalkulation_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
                                    mime="application/pdf",
                                    use_container_width=True
                                )
                            st.success("✅ PDF erstellt!")
                    except Exception as e:
                        st.error(f"Fehler: {str(e)}")
        
        # Einkaufsliste CSV Export
        with col2:
            if st.button("📋 Einkaufsliste als CSV", use_container_width=True):
                try:
                    export_data = []
                    for laden, zutaten in st.session_state.einkaufslisten_dict.items():
                        for zutat_info in zutaten.values():
                            export_data.append({
                                "Laden": laden,
                                "Artikel": zutat_info["artikelname"],
                                "Menge": zutat_info["menge"],
                                "Einheit": zutat_info["einheit"],
                                "Kategorie": zutat_info["kategorie"],
                                "Abhaken": "☐"
                            })
                    
                    df = pd.DataFrame(export_data)
                    csv = df.to_csv(index=False, encoding='utf-8-sig')
                    st.download_button(
                        label="⬇️ Herunterladen",
                        data=csv,
                        file_name=f"Einkaufsliste_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                        mime="text/csv",
                        use_container_width=True
                    )
                    st.success("✅ CSV erstellt!")
                except Exception as e:
                    st.error(f"Fehler: {str(e)}")
        
        # Statistiken
        with col3:
            if st.button("📊 Statistiken exportieren", use_container_width=True):
                try:
                    stats = {
                        "Wochentage": len(st.session_state.tage),
                        "Läden": len(läden_list),
                        "Artikel gesamt": sum(len(items) for items in st.session_state.einkaufslisten_dict.values()),
                        "Lieferanten": len(lieferanten_list),
                        "Export Zeit": datetime.now().isoformat()
                    }
                    
                    st.json(stats)
                    st.download_button(
                        label="⬇️ JSON exportieren",
                        data=json.dumps(stats, indent=2),
                        file_name=f"Statistiken_{datetime.now().strftime('%Y%m%d_%H%M')}.json",
                        mime="application/json",
                        use_container_width=True
                    )
                except Exception as e:
                    st.error(f"Fehler: {str(e)}")
    
    # ============= TAB 5: EINSTELLUNGEN =============
    with tab5:
        st.header("⚙️ Erweiterte Einstellungen")
        
        st.subheader("💾 Session Verwaltung")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🔄 Neuladen", use_container_width=True):
                st.rerun()
        
        with col2:
            if st.button("🗑️ Alle Änderungen zurücksetzen", use_container_width=True):
                st.session_state.artikel_modifikationen = {}
                st.session_state.abgehakte_artikel = {}
                st.session_state.neue_artikel = []
                st.success("✅ Zurückgesetzt!")
                st.rerun()
        
        st.divider()
        st.subheader("📋 Session Informationen")
        
        info_data = {
            "Datum/Zeit": datetime.now().isoformat(),
            "Wochentage": len(st.session_state.tage) if st.session_state.tage else 0,
            "Läden": len(läden_list),
            "Artikel gesamt": sum(len(items) for items in st.session_state.einkaufslisten_dict.values()),
            "Geänderte Artikel": len(st.session_state.artikel_modifikationen),
            "Abgehakte Artikel": sum(len(items) for items in st.session_state.abgehakte_artikel.values())
        }
        
        df_info = pd.DataFrame(list(info_data.items()), columns=["Eigenschaft", "Wert"])
        st.dataframe(df_info, use_container_width=True, hide_index=True)
        
        st.divider()
        st.subheader("🔧 Debug Info")
        if st.checkbox("Debug Modus aktivieren"):
            st.write("Session State:")
            st.write(f"- Tage: {len(st.session_state.tage) if st.session_state.tage else 'None'}")
            st.write(f"- Einkaufslisten: {list(st.session_state.einkaufslisten_dict.keys())}")
            st.write(f"- Modifikationen: {st.session_state.artikel_modifikationen}")
            st.write(f"- Abgehakt: {st.session_state.abgehakte_artikel}")

# ============= FOOTER =============
st.divider()
col_footer1, col_footer2, col_footer3 = st.columns(3)

with col_footer1:
    st.caption("🧑‍💻 Zeltlager SUKU Essensplanung")

with col_footer2:
    st.caption("Streamlit Advanced Edition")

with col_footer3:
    st.caption(f"⏰ {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}")
