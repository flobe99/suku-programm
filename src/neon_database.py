"""
Neon Database Integration für Zeltlager SUKU Planung
Speichert alle Änderungen in einer PostgreSQL Datenbank (gehostet auf Neon)
"""

import os
import json
from datetime import datetime
from typing import Dict, List, Optional
import streamlit as st

try:
    from sqlalchemy import create_engine, Column, String, Integer, DateTime, Text, JSON
    from sqlalchemy.ext.declarative import declarative_base
    from sqlalchemy.orm import sessionmaker
    SQLALCHEMY_AVAILABLE = True
except ImportError:
    SQLALCHEMY_AVAILABLE = False

# Database Configuration
Base = declarative_base()

class ShoppingSession(Base):
    """Model für Einkaufssessions"""
    __tablename__ = 'shopping_sessions'
    
    id = Column(Integer, primary_key=True)
    session_id = Column(String(50), unique=True, nullable=False)
    week_name = Column(String(100), nullable=False)
    checked_items = Column(JSON, default={})
    modified_items = Column(JSON, default={})
    new_items = Column(JSON, default={})
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    def to_dict(self):
        return {
            'id': self.id,
            'session_id': self.session_id,
            'week_name': self.week_name,
            'checked_items': self.checked_items or {},
            'modified_items': self.modified_items or {},
            'new_items': self.new_items or {},
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class NeonDatabase:
    """Wrapper für Neon Database Operationen"""
    
    def __init__(self, database_url: Optional[str] = None):
        """Initialize the database connection"""
        if not SQLALCHEMY_AVAILABLE:
            raise ImportError("SQLAlchemy nicht installiert. Führen Sie aus: pip install -r requirements-streamlit.txt")
        
        # Database URL aus Environment oder Parameter
        self.database_url = database_url or os.getenv('DATABASE_URL')
        
        if not self.database_url:
            raise ValueError(
                "DATABASE_URL nicht gesetzt! Setzen Sie die Umgebungsvariable oder übergeben Sie die URL.\n"
                "Beispiel: DATABASE_URL=postgresql://user:password@host/dbname"
            )
        
        # Konvertiere postgres:// zu postgresql:// für neuere SQLAlchemy Versionen
        if self.database_url.startswith('postgres://'):
            self.database_url = self.database_url.replace('postgres://', 'postgresql://', 1)
        
        # Entferne problematische Parameter
        # if 'channel_binding=require' in self.database_url:
        #     self.database_url = self.database_url.replace('&channel_binding=require', '')
        #     self.database_url = self.database_url.replace('?channel_binding=require', '?sslmode=require')
        
        try:
            # Verwende connection pool mit besseren Settings
            from sqlalchemy.pool import QueuePool
            self.engine = create_engine(
                self.database_url,
                echo=False,
                poolclass=QueuePool,
                pool_size=5,
                max_overflow=10,
                pool_pre_ping=True,
                pool_recycle=3600
            )
            self.Session = sessionmaker(bind=self.engine)
            
            # Test connection
            with self.engine.connect() as conn:
                conn.execute("SELECT 1")
            
            # Erstelle Tabellen falls nicht vorhanden
            Base.metadata.create_all(self.engine)
        except Exception as e:
            error_msg = str(e)
            
            # Hilfreiche Fehlerdiagnose
            diagnostics = []
            
            if "does not exist" in error_msg:
                diagnostics.append("🔴 Datenbank existiert nicht - überprüfen Sie den DB-Namen")
            
            if "invalid password" in error_msg.lower() or "authentication failed" in error_msg.lower():
                diagnostics.append("🔴 Passwort ungültig - überprüfen Sie Credentials in der Neon-Konsole")
            
            raise ConnectionError(
                f"❌ Fehler beim Verbinden zur Neon Datenbank:\n\n"
                f"**Fehler:** {error_msg}\n\n"
                f"**Diagnostik:**\n" + 
                "\n".join("• " + d for d in diagnostics) if diagnostics else "• Unbekannter Fehler" +
                "\n\n**Lösung:**\n"
                "1. Öffnen Sie https://console.neon.tech/\n"
                "2. Wählen Sie Ihr Projekt und die Datenbank\n"
                "3. Kopieren Sie die Connection String\n"
                "4. Fügen Sie sie in `.streamlit/secrets.toml` als DATABASE_URL ein\n"
                "5. Starten Sie die App neu"
            )
    
    def save_session(self, session_id: str, week_name: str, data: Dict) -> bool:
        """Speichert oder aktualisiert eine Shopping-Session"""
        try:
            session = self.Session()
            
            # Suche existierende Session
            existing = session.query(ShoppingSession).filter_by(session_id=session_id).first()
            
            if existing:
                # Update
                existing.week_name = week_name
                existing.checked_items = data.get('abgehakte_artikel', {})
                existing.modified_items = data.get('artikel_modifikationen', {})
                existing.new_items = data.get('neue_artikel', [])
                existing.updated_at = datetime.now()
            else:
                # Create new
                new_session = ShoppingSession(
                    session_id=session_id,
                    week_name=week_name,
                    checked_items=data.get('abgehakte_artikel', {}),
                    modified_items=data.get('artikel_modifikationen', {}),
                    new_items=data.get('neue_artikel', [])
                )
                session.add(new_session)
            
            session.commit()
            session.close()
            return True
        except Exception as e:
            st.error(f"Datenbankfehler beim Speichern: {str(e)}")
            return False
    
    def load_session(self, session_id: str) -> Optional[Dict]:
        """Lädt eine Shopping-Session aus der Datenbank"""
        try:
            session = self.Session()
            shopping_session = session.query(ShoppingSession).filter_by(session_id=session_id).first()
            session.close()
            
            if shopping_session:
                return {
                    'abgehakte_artikel': shopping_session.checked_items or {},
                    'artikel_modifikationen': shopping_session.modified_items or {},
                    'neue_artikel': shopping_session.new_items or [],
                    'updated_at': shopping_session.updated_at.isoformat() if shopping_session.updated_at else None
                }
        except Exception as e:
            st.warning(f"Fehler beim Laden aus Datenbank: {str(e)}")
        
        return None
    
    def list_sessions(self) -> List[Dict]:
        """Listet alle Shopping-Sessions auf"""
        try:
            session = self.Session()
            sessions = session.query(ShoppingSession).all()
            session.close()
            
            return [s.to_dict() for s in sessions]
        except Exception as e:
            st.warning(f"Fehler beim Auflisten der Sessions: {str(e)}")
            return []
    
    def delete_session(self, session_id: str) -> bool:
        """Löscht eine Shopping-Session"""
        try:
            session = self.Session()
            session.query(ShoppingSession).filter_by(session_id=session_id).delete()
            session.commit()
            session.close()
            return True
        except Exception as e:
            st.error(f"Fehler beim Löschen: {str(e)}")
            return False
    
    def get_db_status(self) -> Dict:
        """Gibt Status der Datenbankverbindung zurück"""
        try:
            session = self.Session()
            count = session.query(ShoppingSession).count()
            session.close()
            
            return {
                'connected': True,
                'session_count': count,
                'error': None
            }
        except Exception as e:
            return {
                'connected': False,
                'session_count': 0,
                'error': str(e)
            }

def get_neon_db() -> Optional[NeonDatabase]:
    """Gibt die Neon Database Instanz zur\u00fcck (mit Caching)"""
    if 'neon_db' not in st.session_state:
        try:
            db_url = os.getenv('DATABASE_URL') or st.secrets.get('DATABASE_URL')
            if db_url:
                st.session_state.neon_db = NeonDatabase(db_url)
            else:
                return None
        except Exception as e:
            st.error(f"Datenbankverbindung fehlgeschlagen: {str(e)}")
            return None
    
    return st.session_state.neon_db