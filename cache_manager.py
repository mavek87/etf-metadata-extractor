"""
Modulo per la gestione di cache in memoria e persistente con timestamp automatici.
Supporta TTL flessibili tramite utility helper e valori JSON di grandi dimensioni.
"""

import json
import sqlite3
import threading
import time
from pathlib import Path
from typing import Any, Optional, Dict, Set, Tuple, Callable
from contextlib import contextmanager
from datetime import datetime, timedelta


class CacheEntry:
    """Rappresenta una entry della cache con timestamp."""

    def __init__(self, value: Any, timestamp: float = None):
        self.value = value
        self.timestamp = timestamp or time.time()

    def age_seconds(self) -> float:
        """Restituisce l'età dell'entry in secondi."""
        return time.time() - self.timestamp

    def to_dict(self) -> Dict[str, Any]:
        """Converte l'entry in dizionario."""
        return {
            'value': self.value,
            'timestamp': self.timestamp,
            'age_seconds': self.age_seconds()
        }


class MemoryCache:
    """Cache in memoria thread-safe basata su dizionario con timestamp."""

    def __init__(self):
        self._cache: Dict[str, CacheEntry] = {}
        self._lock = threading.RLock()

    def get(self, key: str) -> Optional[Any]:
        """Recupera un valore dalla cache."""
        with self._lock:
            entry = self._cache.get(key)
            return entry.value if entry else None

    def get_with_info(self, key: str) -> Optional[Dict[str, Any]]:
        """Recupera valore con informazioni complete (valore, timestamp, età)."""
        with self._lock:
            entry = self._cache.get(key)
            return entry.to_dict() if entry else None

    def set(self, key: str, value: Any) -> None:
        """Scrive un valore nella cache con timestamp corrente."""
        with self._lock:
            self._cache[key] = CacheEntry(value)

    def exists(self, key: str) -> bool:
        """Verifica se una chiave esiste nella cache."""
        with self._lock:
            return key in self._cache

    def delete(self, key: str) -> bool:
        """Cancella una chiave dalla cache. Restituisce True se esisteva."""
        with self._lock:
            return self._cache.pop(key, None) is not None

    def clear(self) -> None:
        """Cancella tutta la cache."""
        with self._lock:
            self._cache.clear()

    def keys(self) -> Set[str]:
        """Restituisce tutte le chiavi presenti."""
        with self._lock:
            return set(self._cache.keys())

    def size(self) -> int:
        """Restituisce il numero di elementi in cache."""
        with self._lock:
            return len(self._cache)

    def get_age(self, key: str) -> Optional[float]:
        """Restituisce l'età di una entry in secondi."""
        with self._lock:
            entry = self._cache.get(key)
            return entry.age_seconds() if entry else None

    def get_timestamp(self, key: str) -> Optional[float]:
        """Restituisce il timestamp di una entry."""
        with self._lock:
            entry = self._cache.get(key)
            return entry.timestamp if entry else None


class PersistentCache:
    """Cache persistente basata su SQLite con supporto per JSON e timestamp."""

    def __init__(self, db_path: str = "cache.db"):
        self.db_path = Path(db_path)
        self._lock = threading.RLock()
        self._init_db()

    def _init_db(self) -> None:
        """Inizializza il database SQLite."""
        with self._get_connection() as conn:
            conn.execute("""
                         CREATE TABLE IF NOT EXISTS cache (
                                                              key TEXT PRIMARY KEY,
                                                              value BLOB NOT NULL,
                                                              timestamp REAL NOT NULL,
                                                              created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                         )
                         """)
            conn.execute("""
                         CREATE INDEX IF NOT EXISTS idx_timestamp ON cache(timestamp)
                         """)
            conn.execute("""
                         CREATE INDEX IF NOT EXISTS idx_created_at ON cache(created_at)
                         """)

    @contextmanager
    def _get_connection(self):
        """Context manager per la connessione al database."""
        conn = sqlite3.connect(self.db_path, timeout=30)
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def get(self, key: str) -> Optional[Any]:
        """Recupera un valore dalla cache."""
        with self._lock:
            with self._get_connection() as conn:
                cursor = conn.execute(
                    "SELECT value FROM cache WHERE key = ?", (key,)
                )
                row = cursor.fetchone()
                if row:
                    return json.loads(row[0].decode('utf-8'))
                return None

    def get_with_info(self, key: str) -> Optional[Dict[str, Any]]:
        """Recupera valore con informazioni complete."""
        with self._lock:
            with self._get_connection() as conn:
                cursor = conn.execute(
                    "SELECT value, timestamp FROM cache WHERE key = ?", (key,)
                )
                row = cursor.fetchone()
                if row:
                    value = json.loads(row[0].decode('utf-8'))
                    timestamp = row[1]
                    age_seconds = time.time() - timestamp
                    return {
                        'value': value,
                        'timestamp': timestamp,
                        'age_seconds': age_seconds
                    }
                return None

    def set(self, key: str, value: Any) -> None:
        """Scrive un valore nella cache con timestamp corrente."""
        json_data = json.dumps(value, ensure_ascii=False, separators=(',', ':'))
        blob_data = json_data.encode('utf-8')
        timestamp = time.time()

        with self._lock:
            with self._get_connection() as conn:
                conn.execute("""
                    INSERT OR REPLACE INTO cache (key, value, timestamp) 
                    VALUES (?, ?, ?)
                """, (key, blob_data, timestamp))

    def exists(self, key: str) -> bool:
        """Verifica se una chiave esiste nella cache."""
        with self._lock:
            with self._get_connection() as conn:
                cursor = conn.execute(
                    "SELECT 1 FROM cache WHERE key = ? LIMIT 1", (key,)
                )
                return cursor.fetchone() is not None

    def delete(self, key: str) -> bool:
        """Cancella una chiave dalla cache. Restituisce True se esisteva."""
        with self._lock:
            with self._get_connection() as conn:
                cursor = conn.execute(
                    "DELETE FROM cache WHERE key = ?", (key,)
                )
                return cursor.rowcount > 0

    def clear(self) -> None:
        """Cancella tutta la cache."""
        with self._lock:
            with self._get_connection() as conn:
                conn.execute("DELETE FROM cache")

    def keys(self) -> Set[str]:
        """Restituisce tutte le chiavi presenti."""
        with self._lock:
            with self._get_connection() as conn:
                cursor = conn.execute("SELECT key FROM cache")
                return {row[0] for row in cursor.fetchall()}

    def size(self) -> int:
        """Restituisce il numero di elementi in cache."""
        with self._lock:
            with self._get_connection() as conn:
                cursor = conn.execute("SELECT COUNT(*) FROM cache")
                return cursor.fetchone()[0]

    def get_age(self, key: str) -> Optional[float]:
        """Restituisce l'età di una entry in secondi."""
        with self._lock:
            with self._get_connection() as conn:
                cursor = conn.execute(
                    "SELECT timestamp FROM cache WHERE key = ?", (key,)
                )
                row = cursor.fetchone()
                if row:
                    return time.time() - row[0]
                return None

    def get_timestamp(self, key: str) -> Optional[float]:
        """Restituisce il timestamp di una entry."""
        with self._lock:
            with self._get_connection() as conn:
                cursor = conn.execute(
                    "SELECT timestamp FROM cache WHERE key = ?", (key,)
                )
                row = cursor.fetchone()
                return row[0] if row else None

    def cleanup_old_entries(self, days: int = 30) -> int:
        """Rimuove le entry più vecchie del numero di giorni specificato."""
        with self._lock:
            with self._get_connection() as conn:
                cursor = conn.execute("""
                    DELETE FROM cache 
                    WHERE created_at < datetime('now', '-{} days')
                """.format(days))
                return cursor.rowcount


class CacheManager:
    """
    Gestisce sia cache in memoria che persistente con un'interfaccia unificata.
    Include timestamp automatici per ogni entry.
    """

    def __init__(self, use_persistent: bool = False, db_path: str = "cache.db"):
        """
        Inizializza il gestore cache.

        Args:
            use_persistent: Se True usa cache persistente, altrimenti memoria
            db_path: Percorso del database SQLite (solo per cache persistente)
        """
        if use_persistent:
            self._cache = PersistentCache(db_path)
        else:
            self._cache = MemoryCache()

        self.is_persistent = use_persistent

    def get(self, key: str, default: Any = None) -> Any:
        """
        Recupera un valore dalla cache.

        Args:
            key: Chiave da cercare
            default: Valore di default se la chiave non esiste

        Returns:
            Valore associato alla chiave o default
        """
        value = self._cache.get(key)
        return value if value is not None else default

    def get_with_info(self, key: str, default: Any = None) -> Optional[Dict[str, Any]]:
        """
        Recupera un valore con tutte le informazioni (valore, timestamp, età).

        Args:
            key: Chiave da cercare
            default: Valore di default se la chiave non esiste

        Returns:
            Dizionario con 'value', 'timestamp', 'age_seconds' o None
        """
        info = self._cache.get_with_info(key)
        if info is None and default is not None:
            return {'value': default, 'timestamp': None, 'age_seconds': None}
        return info

    def set(self, key: str, value: Any) -> None:
        """
        Scrive un valore nella cache con timestamp automatico.

        Args:
            key: Chiave
            value: Valore (deve essere serializzabile in JSON)
        """
        self._cache.set(key, value)

    def exists(self, key: str) -> bool:
        """
        Verifica se una chiave esiste nella cache.

        Args:
            key: Chiave da verificare

        Returns:
            True se la chiave esiste
        """
        return self._cache.exists(key)

    def delete(self, key: str) -> bool:
        """
        Cancella una chiave dalla cache.

        Args:
            key: Chiave da cancellare

        Returns:
            True se la chiave esisteva ed è stata cancellata
        """
        return self._cache.delete(key)

    def clear(self) -> None:
        """Cancella tutta la cache."""
        self._cache.clear()

    def keys(self) -> Set[str]:
        """
        Restituisce tutte le chiavi presenti.

        Returns:
            Set con tutte le chiavi
        """
        return self._cache.keys()

    def size(self) -> int:
        """
        Restituisce il numero di elementi in cache.

        Returns:
            Numero di elementi
        """
        return self._cache.size()

    def get_age(self, key: str) -> Optional[float]:
        """
        Restituisce l'età di una entry in secondi.

        Args:
            key: Chiave da verificare

        Returns:
            Età in secondi o None se la chiave non esiste
        """
        return self._cache.get_age(key)

    def get_timestamp(self, key: str) -> Optional[float]:
        """
        Restituisce il timestamp di una entry.

        Args:
            key: Chiave da verificare

        Returns:
            Timestamp Unix o None se la chiave non esiste
        """
        return self._cache.get_timestamp(key)

    def get_or_set(self, key: str, factory_func: Callable, *args, **kwargs) -> Any:
        """
        Recupera un valore o lo crea usando una funzione factory.
        (se esiste prendilo, altrimenti crealo)

        Args:
            key: Chiave da cercare
            factory_func: Funzione da chiamare per creare il valore se non esiste
            *args, **kwargs: Argomenti per la factory function

        Returns:
            Valore dalla cache o creato dalla factory function
        """
        if self.exists(key):
            return self.get(key)

        value = factory_func(*args, **kwargs)
        self.set(key, value)
        return value

    # === METODI TTL HELPER ===

    def is_expired(self, key: str, ttl_seconds: float) -> bool:
        """
        Verifica se una entry è scaduta secondo il TTL specificato.

        Args:
            key: Chiave da controllare
            ttl_seconds: TTL in secondi

        Returns:
            True se la entry è scaduta o non esiste
        """
        age = self.get_age(key)
        return age is None or age > ttl_seconds

    def get_if_fresh(self, key: str, ttl_seconds: float, default: Any = None) -> Any:
        """
        Recupera un valore solo se è più fresco del TTL specificato.

        Args:
            key: Chiave da recuperare
            ttl_seconds: TTL massimo in secondi
            default: Valore se scaduto o non esistente

        Returns:
            Valore se fresco, default se scaduto/inesistente
        """
        if self.is_expired(key, ttl_seconds):
            return default
        return self.get(key, default)

    def get_or_set_if_stale(self, key: str, factory_func: Callable,
                            ttl_seconds: float, *args, **kwargs) -> Any:
        """
        Pattern cache-aside con TTL: restituisce il valore cached se fresco,
        altrimenti lo ricarica usando factory_func.

        (Se è fresco prendilo, se è scaduto ricaricalo)

        Args:
            key: Chiave
            factory_func: Funzione per ricaricare il valore
            ttl_seconds: TTL in secondi
            *args, **kwargs: Argomenti per factory_func

        Returns:
            Valore fresco dalla cache o ricaricato
        """
        if not self.is_expired(key, ttl_seconds):
            return self.get(key)

        # Ricarica il valore
        fresh_value = factory_func(*args, **kwargs)
        self.set(key, fresh_value)
        return fresh_value

    def cleanup_expired_keys(self, ttl_seconds: float) -> int:
        """
        Rimuove tutte le chiavi scadute dalla cache.

        Args:
            ttl_seconds: TTL per considerare una entry scaduta

        Returns:
            Numero di chiavi rimosse
        """
        removed_count = 0
        keys_to_remove = []

        for key in self.keys():
            if self.is_expired(key, ttl_seconds):
                keys_to_remove.append(key)

        for key in keys_to_remove:
            if self.delete(key):
                removed_count += 1

        return removed_count


# Istanze globali per facilità d'uso
memory_cache = CacheManager(use_persistent=False)
persistent_cache = CacheManager(use_persistent=True)


# === ESEMPI DI UTILIZZO ===

if __name__ == "__main__":
    print("=== Test Cache con Timestamp ===")

    # Cache in memoria
    cache = CacheManager(use_persistent=True)

    # 1. Uso base con timestamp automatico
    cache.set("user:123", {"name": "Mario", "age": 30})

    print(f"Valore: {cache.get('user:123')}")
    print(f"Età entry: {cache.get_age('user:123'):.2f} secondi")
    print(f"Info complete: {cache.get_with_info('user:123')}")

    # Aspetta un secondo per vedere il cambio di età
    import time
    time.sleep(1)
    print(f"Età dopo 1 sec: {cache.get_age('user:123'):.2f} secondi")

    print("\n=== Test TTL Helper Functions ===")

    # 2. TTL con utility functions
    TTL_5_SECONDS = 5.0

    # Carica dato iniziale
    cache.set("api_data", {"data": "valore importante", "loaded_at": time.time()})

    # Controlla se è fresco (dovrebbe essere True)
    fresh_data = cache.get_if_fresh("api_data", TTL_5_SECONDS, "DEFAULT")
    print(f"Dato fresco: {fresh_data}")

    # Simula attesa di 6 secondi
    print("Simulo TTL scaduto...")
    time.sleep(0.1)  # Breve per il demo

    # Usa pattern cache-aside con ricarica automatica
    def load_api_data():
        print("⚡ Ricarico dati dall'API...")
        return {"data": "nuovo valore", "loaded_at": time.time()}

    # Se scaduto, ricarica automaticamente
    fresh_data = cache.get_or_set_if_stale("api_data", load_api_data, 0.05)  # TTL molto breve per demo
    print(f"Dato aggiornato: {fresh_data}")

    print("\n=== Esempio Pratico ===")

    def fetch_user_profile(user_id):
        """Simula chiamata API costosa."""
        print(f"🌐 Carico profilo utente {user_id} dall'API...")
        time.sleep(0.1)  # Simula latenza
        return {
            "id": user_id,
            "name": f"User {user_id}",
            "email": f"user{user_id}@example.com",
            "last_login": time.time()
        }

    USER_CACHE_TTL = 300  # 5 minuti in produzione

    # Prima chiamata - carica dall'API
    profile = cache.get_or_set_if_stale(
        "profile:456",
        fetch_user_profile, USER_CACHE_TTL,
        user_id=456
    )
    print(f"Profilo: {profile}")

    # Seconda chiamata - dalla cache (nessun caricamento)
    profile = cache.get_or_set_if_stale(
        "profile:456",
        fetch_user_profile, USER_CACHE_TTL,
        user_id=456
    )
    print("✅ Seconda chiamata - dalla cache (nessun log API)")

    # # Test cleanup expired keys
    # print(f"\n🧹 Cleanup chiavi scadute: {cache.cleanup_expired_keys(0.01)} rimosse")
    #
    # # Cleanup finale
    # cache.clear()
    # print("\n🧹 Cache pulita!")