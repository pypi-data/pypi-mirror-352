import tinykv
import sqlite3
from typing import Any, Dict, List, Optional
import os


class KVStoreController:
    def __init__(self, db_path: str):
        """Initialize KV store
        Args:
            db_path: Path to the database file
        """
        self.db_path = db_path

        # Connect to disk database
        self._disk_conn: sqlite3.Connection = sqlite3.connect(self.db_path, timeout=1)

        # Create schema in disk database (IF NOT EXISTS)
        if not self._table_exists(self._disk_conn, "kv"):
            tinykv.create_schema(self._disk_conn)

        # Connect to in-memory database
        self._memory_conn = sqlite3.connect(":memory:")

        # Load data from disk DB to in-memory DB
        with self._disk_conn:
            self._disk_conn.backup(self._memory_conn)

        # Initialize TinyKV object based on in-memory DB
        self._kv = tinykv.TinyKV(self._memory_conn)

    def _table_exists(self, conn: sqlite3.Connection, table_name: str) -> bool:
        """Check if table exists"""
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table_name,))
        return cursor.fetchone() is not None

    def _table_drop(self, table_name: str) -> None:
        """Drop table"""
        cursor = self._disk_conn.cursor()
        cursor.execute(f"DROP TABLE IF EXISTS {table_name}")
        self._disk_conn.commit()

    def reset_db(self) -> None:
        """Reset database"""
        try:
            # Close existing connections to avoid conflicts
            self._disk_conn.commit()
            self._memory_conn.commit()
            self._disk_conn.close()
            self._memory_conn.close()

            # Reconnect to databases
            self._disk_conn = sqlite3.connect(self.db_path)
            self._memory_conn = sqlite3.connect(':memory:')

            # Drop existing table and recreate schema
            self._table_drop("kv")
            tinykv.create_schema(self._disk_conn)

            # Perform backup operation safely
            with self._disk_conn:
                self._disk_conn.backup(self._memory_conn)

            self._kv = tinykv.TinyKV(self._memory_conn)
        except Exception as e:
            if e == sqlite3.OperationalError:
                print(f"Database reset error: {e}")
            elif e == Exception:
                print(f"Unexpected error during database reset: {e}")

            if self._disk_conn:
                self._disk_conn.close()
            if self._memory_conn:
                self._memory_conn.close()

    def remove_db(self) -> None:
        """Remove database file"""
        self._table_drop("kv")
        self._disk_conn.close()
        self._memory_conn.close()
        os.remove(self.db_path)

    def set(self, key: str, value: Any) -> None:
        """Store value (reflect in in-memory DB)"""
        self._kv.set(key, value)

    def get(self, key: str, default: Any = None) -> Any:
        """Retrieve value (from in-memory DB)"""
        return self._kv.get(key, default)

    def delete(self, key: str) -> None:
        """Delete value (reflect in in-memory DB)"""
        if key in self._kv:
            del self._kv[key]

    def set_many(self, items: Dict[str, Any]) -> None:
        """Store multiple values (reflect in in-memory DB)"""
        self._kv.set_many(items)

    def get_many(self, keys: List[str]) -> Dict[str, Any]:
        """Retrieve multiple values (from in-memory DB)"""
        return self._kv.get_many(keys)

    def exists(self, key: str) -> bool:
        """Check if key exists"""
        try:
            self._kv.get(key)
            return True
        except KeyError:
            return False

    def clear(self) -> None:
        """Delete all data (reflect in in-memory DB)"""
        for key in list(self._kv.keys()):
            del self._kv[key]

    def save_to_disk(self) -> None:
        """Backup in-memory DB content to disk DB"""
        try:
            self._memory_conn.commit()  # Commit in-memory DB transaction
            with self._disk_conn:
                # Backup in-memory DB to disk DB
                self._memory_conn.backup(self._disk_conn, pages=100, progress=self._backup_progress)
            print("Data successfully saved to disk.")
        except sqlite3.OperationalError as e:
            print(f"Failed to save to disk: {e}")

    def _backup_progress(self, status, remaining, total):
        """Display backup progress"""
        print(f"Backup progress: {total - remaining}/{total} pages copied")

    def close(self) -> None:
        """Close database connections"""
        # Save in-memory to disk before closing
        self.save_to_disk()

        # Close connections
        self._memory_conn.close()
        self._disk_conn.close()
        del self._kv


# Test code
if __name__ == "__main__":
    kv_controller = KVStoreController("device_config.db")

    # Store values
    kv_controller.set("device_id", "device_001")
    kv_controller.set("connection_info", {"hub_ip": "192.168.1.100", "port": 8080})
    kv_controller.set_many({"wifi_ssid": "MyNetwork", "wifi_password": "secure123"})

    # Retrieve values
    device_id = kv_controller.get("device_id")
    conn_info = kv_controller.get("connection_info")
    print("device_id:", device_id)
    print("connection_info:", conn_info)

    # Retrieve multiple values
    wifi_info = kv_controller.get_many(["wifi_ssid", "wifi_password"])
    print("wifi_info:", wifi_info)

    # In-memory DB content is reflected on disk upon closing
    kv_controller.close()
