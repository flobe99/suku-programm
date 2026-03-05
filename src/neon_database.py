"""
Neon Database Integration mit Data API (HTTP REST)
Speichert alle Änderungen in einer PostgreSQL Datenbank (gehostet auf Neon)
Verwendet HTTP REST API statt direkter PostgreSQL Verbindung
"""

import os
import json
import requests
from datetime import datetime
from typing import Dict, List, Optional
import streamlit as st


class NeonDatabaseConnection:
    """Streamlit Connection für Neon Data API"""
    
    def __init__(self, api_url: str, api_key: str):
        """Initialize the Data API connection"""
        self.api_url = api_url.rstrip('/')
        self.api_key = api_key
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        # Test connection
        try:
            self._test_connection()
        except Exception as e:
            raise ConnectionError(f"❌ Neon Data API Verbindung fehlgeschlagen: {str(e)}")
    
    def _test_connection(self):
        """Test the connection to Data API"""
        try:
            # Versuche, die Tabelle zu beschreiben
            response = requests.get(
                f"{self.api_url}/tables/shopping_sessions",
                headers=self.headers,
                timeout=5
            )
            if response.status_code not in [200, 400]:  # 400 könnte bedeuten: Tabelle existiert nicht
                raise Exception(f"Status Code: {response.status_code}")
        except Exception as e:
            raise ConnectionError(f"Data API nicht erreichbar: {str(e)}")
    
    def save_session(self, session_id: str, week_name: str, data: Dict) -> bool:
        """Speichert oder aktualisiert eine Shopping-Session"""
        try:
            payload = {
                "session_id": session_id,
                "week_name": week_name,
                "checked_items": json.dumps(data.get('abgehakte_artikel', {})),
                "modified_items": json.dumps(data.get('artikel_modifikationen', {})),
                "new_items": json.dumps(data.get('neue_artikel', [])),
                "updated_at": datetime.now().isoformat()
            }
            
            # Überprüfe zuerst, ob die Session existiert
            existing = self._get_raw_session(session_id)
            
            if existing:
                # Update: DELETE alte + INSERT neue
                self._delete_raw_session(session_id)
            
            # Insert neue Session
            response = requests.post(
                f"{self.api_url}/tables/shopping_sessions/rows",
                headers=self.headers,
                json=payload,
                timeout=10
            )
            
            if response.status_code in [200, 201]:
                return True
            else:
                error_msg = response.text if response.text else f"Status {response.status_code}"
                st.error(f"API Fehler beim Speichern: {error_msg}")
                return False
                
        except Exception as e:
            st.error(f"Fehler beim Speichern der Session: {str(e)}")
            return False
    
    def load_session(self, session_id: str) -> Optional[Dict]:
        """Lädt eine Shopping-Session aus der Datenbank"""
        try:
            raw_data = self._get_raw_session(session_id)
            
            if raw_data:
                # Parse JSON fields
                return {
                    'abgehakte_artikel': json.loads(raw_data.get('checked_items', '{}')),
                    'artikel_modifikationen': json.loads(raw_data.get('modified_items', '{}')),
                    'neue_artikel': json.loads(raw_data.get('new_items', '[]')),
                    'updated_at': raw_data.get('updated_at')
                }
        except Exception as e:
            st.warning(f"Fehler beim Laden aus Datenbank: {str(e)}")
        
        return None
    
    def _get_raw_session(self, session_id: str) -> Optional[Dict]:
        """Lädt raw Session-Daten (intern)"""
        try:
            params = {
                "session_id": f"eq.{session_id}"
            }
            
            response = requests.get(
                f"{self.api_url}/tables/shopping_sessions/rows",
                headers=self.headers,
                params=params,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list) and len(data) > 0:
                    return data[0]
            
            return None
        except Exception as e:
            st.warning(f"Fehler beim Abrufen der Session: {str(e)}")
            return None
    
    def _delete_raw_session(self, session_id: str) -> bool:
        """Löscht eine raw Session (intern)"""
        try:
            params = {
                "session_id": f"eq.{session_id}"
            }
            
            response = requests.delete(
                f"{self.api_url}/tables/shopping_sessions/rows",
                headers=self.headers,
                params=params,
                timeout=10
            )
            
            return response.status_code in [200, 204]
        except Exception as e:
            return False
    
    def list_sessions(self) -> List[Dict]:
        """Listet alle Shopping-Sessions auf"""
        try:
            response = requests.get(
                f"{self.api_url}/tables/shopping_sessions/rows",
                headers=self.headers,
                timeout=10
            )
            
            if response.status_code == 200:
                sessions = response.json()
                if isinstance(sessions, list):
                    result = []
                    for s in sessions:
                        result.append({
                            'id': s.get('id'),
                            'session_id': s.get('session_id'),
                            'week_name': s.get('week_name'),
                            'checked_items': json.loads(s.get('checked_items', '{}')),
                            'modified_items': json.loads(s.get('modified_items', '{}')),
                            'new_items': json.loads(s.get('new_items', '[]')),
                            'created_at': s.get('created_at'),
                            'updated_at': s.get('updated_at')
                        })
                    return result
            return []
        except Exception as e:
            st.warning(f"Fehler beim Auflisten der Sessions: {str(e)}")
            return []
    
    def delete_session(self, session_id: str) -> bool:
        """Löscht eine Shopping-Session"""
        try:
            params = {
                "session_id": f"eq.{session_id}"
            }
            
            response = requests.delete(
                f"{self.api_url}/tables/shopping_sessions/rows",
                headers=self.headers,
                params=params,
                timeout=10
            )
            
            if response.status_code in [200, 204]:
                return True
            else:
                st.error(f"Fehler beim Löschen: Status {response.status_code}")
                return False
        except Exception as e:
            st.error(f"Fehler beim Löschen: {str(e)}")
            return False
    
    def get_db_status(self) -> Dict:
        """Gibt Status der Datenbankverbindung zurück"""
        try:
            response = requests.get(
                f"{self.api_url}/tables/shopping_sessions/rows",
                headers=self.headers,
                timeout=5
            )
            
            if response.status_code == 200:
                sessions = response.json()
                count = len(sessions) if isinstance(sessions, list) else 0
                return {
                    'connected': True,
                    'session_count': count,
                    'error': None
                }
            else:
                return {
                    'connected': False,
                    'session_count': 0,
                    'error': f"Status {response.status_code}"
                }
        except Exception as e:
            return {
                'connected': False,
                'session_count': 0,
                'error': str(e)
            }


def get_neon_db() -> Optional[NeonDatabaseConnection]:
    """Gibt die Neon Database Connection Instanz zurück (mit Caching)"""
    if 'neon_db' not in st.session_state:
        try:
            # Versuche, Credentials aus Secrets zu laden
            api_url = os.getenv('DATA_API_URL') or st.secrets.get('DATA_API_URL')
            api_key = os.getenv('API_KEY') or st.secrets.get('API_KEY')
            
            if not api_url or not api_key:
                st.error(
                    "❌ DATA_API_URL und API_KEY nicht gesetzt!\n\n"
                    "Konfigurieren Sie diese in `.streamlit/secrets.toml`:\n"
                    "```toml\n"
                    'DATA_API_URL="https://..."\n'
                    'API_KEY="napi_..."\n'
                    "```"
                )
                return None
            
            st.session_state.neon_db = NeonDatabaseConnection(api_url, api_key)
        except Exception as e:
            st.error(f"❌ Datenbankverbindung fehlgeschlagen:\n\n{str(e)}")
            return None
    
    return st.session_state.neon_db


# Legacy class names for backwards compatibility
class NeonDatabase(NeonDatabaseConnection):
    """Backwards compatibility alias"""
    pass