import os
import json
import stat
import pathlib
import shutil
import sqlite3
from typing import Any, Optional, Dict, List


class localStoragePyStorageException(Exception):
    pass


class BasicStorageBackend:
    def __init__(self, app_namespace: str) -> None:
        # self.base_storage_path = os.path.join(pathlib.Path.home() , ".config", "LocalStoragePro")
        if app_namespace.count(os.sep) > 0:
            raise localStoragePyStorageException('app_namespace may not contain path separators!')
        self.app_storage_path = os.path.join(pathlib.Path.home() , ".config", "localStoragePro", app_namespace)
        if not os.path.isdir(self.app_storage_path):
            os.makedirs(os.path.join(self.app_storage_path))

    def raise_dummy_exception(self) -> None:
        raise localStoragePyStorageException("Called dummy backend!")

    def get_item(self, item: str) -> Optional[str]:
        self.raise_dummy_exception()
        return None

    def set_item(self, item: str, value: Any) -> None:
        self.raise_dummy_exception()

    def remove_item(self, item: str) -> None:
        self.raise_dummy_exception()

    def get_all(self) -> Dict[str, str]:
        self.raise_dummy_exception()
        return {}

    def get_many(self, items: List[str]) -> Dict[str, str]:
        self.raise_dummy_exception()
        return {}

    def remove_all(self) -> None:
        self.raise_dummy_exception()

    def clear(self) -> None:
        self.raise_dummy_exception()
        

class TextStorageBackend(BasicStorageBackend):
    def __init__(self, app_namespace: str) -> None:
        super().__init__(app_namespace)

    def shutil_error_path(self, func: Any, path: str, exc_info: Any) -> None:
        if not os.access(path, os.W_OK):
            os.chmod(path, stat.S_IWUSR)
        func(path)

    def get_file_path(self, key: str) -> str:
        return os.path.join(self.app_storage_path, key)

    def get_item(self, item: str) -> Optional[str]:
        item_path = self.get_file_path(item)
        if os.path.isfile(item_path):
            with open(item_path, "r") as item_file:
                return str(item_file.read())
        else:
            return None

    def get_all(self) -> Dict[str, str]:
        result = {}
        if os.path.isdir(self.app_storage_path):
            for filename in os.listdir(self.app_storage_path):
                file_path = os.path.join(self.app_storage_path, filename)
                if os.path.isfile(file_path):
                    with open(file_path, "r") as item_file:
                        result[filename] = str(item_file.read())
        return result

    def get_many(self, items: List[str]) -> Dict[str, str]:
        result = {}
        for key in items:
            value = self.get_item(key)
            if value is not None:
                result[key] = value
        return result

    def set_item(self, item: str, value: Any) -> None:
        item_path = self.get_file_path(item)
        with open(item_path, "w") as item_file:
            item_file.write(str(value))

    def remove_item(self, item: str) -> None: 
        item_path = self.get_file_path(item)
        if os.path.isfile(item_path):
            os.remove(item_path)

    def remove_all(self) -> None:
        self.clear()

    def clear(self) -> None:
        if os.path.isdir(self.app_storage_path):
            shutil.rmtree(self.app_storage_path, onerror=self.shutil_error_path)
        os.makedirs(self.app_storage_path)


class SQLiteStorageBackend(BasicStorageBackend):
    def __init__(self, app_namespace: str) -> None:
        super().__init__(app_namespace)
        self.db_path = os.path.join(self.app_storage_path, "localStorageSQLite.db")
        self.db_connection = sqlite3.connect(self.db_path)
        self.db_cursor = self.db_connection.cursor()

        empty = self.db_cursor.execute("SELECT name FROM sqlite_master").fetchall()
        if empty == []:
            self.create_default_tables()

    def create_default_tables(self) -> None:
        self.db_cursor.execute("CREATE TABLE localStoragePro (key TEXT PRIMARY KEY, value TEXT)")
        self.db_connection.commit()
        
    def get_item(self, item: str) -> Optional[str]:
        fetched_value = self.db_cursor.execute("SELECT value FROM localStoragePro WHERE key = ?", (item,)).fetchone()
        if type(fetched_value) is tuple:
            return fetched_value[0]
        else:
            return None

    def get_all(self) -> Dict[str, str]:
        result = {}
        fetched_values = self.db_cursor.execute("SELECT key, value FROM localStoragePro").fetchall()
        for key, value in fetched_values:
            result[key] = value
        return result

    def get_many(self, items: List[str]) -> Dict[str, str]:
        result = {}
        placeholders = ", ".join(["?" for _ in items])
        if not items:
            return result
        query = f"SELECT key, value FROM localStoragePro WHERE key IN ({placeholders})"
        fetched_values = self.db_cursor.execute(query, items).fetchall()
        for key, value in fetched_values:
            result[key] = value
        return result

    def set_item(self, item: str, value: Any) -> None:
        if len(self.db_cursor.execute("SELECT key FROM localStoragePro WHERE key = ?", (item,)).fetchall()) == 0:
            self.db_cursor.execute("INSERT INTO localStoragePro (key, value) VALUES (?, ?)", (item, str(value)))
        else:
            self.db_cursor.execute("UPDATE localStoragePro SET value = ? WHERE key = ?", (str(value), item))
        self.db_connection.commit()

    def remove_item(self, item: str) -> None:
        self.db_cursor.execute("DELETE FROM localStoragePro WHERE key = ?", (item,))
        self.db_connection.commit()

    def remove_all(self) -> None:
        self.db_cursor.execute("DELETE FROM localStoragePro")
        self.db_connection.commit()

    def clear(self) -> None:
        self.db_cursor.execute("DROP TABLE localStoragePro")
        self.create_default_tables()


class JSONStorageBackend(BasicStorageBackend):
    def __init__(self, app_namespace: str) -> None:
        super().__init__(app_namespace)
        self.json_path = os.path.join(self.app_storage_path, "localStorageJSON.json")
        self.json_data: Dict[str, str] = {}

        if not os.path.isfile(self.json_path):
            self.commit_to_disk()

        with open(self.json_path, "r") as json_file:
            self.json_data = json.load(json_file)
        
    def commit_to_disk(self) -> None:
        with open(self.json_path, "w") as json_file:
            json.dump(self.json_data, json_file)

    def get_item(self, item: str) -> Optional[str]:
        if item in self.json_data:
            return self.json_data[item]
        return None

    def get_all(self) -> Dict[str, str]:
        return dict(self.json_data)

    def get_many(self, items: List[str]) -> Dict[str, str]:
        result = {}
        for key in items:
            if key in self.json_data:
                result[key] = self.json_data[key]
        return result

    def set_item(self, item: str, value: Any) -> None:
        self.json_data[item] = str(value)
        self.commit_to_disk()

    def remove_item(self, item: str) -> None: 
        if item in self.json_data:
            del self.json_data[item]
            self.commit_to_disk()

    def remove_all(self) -> None:
        self.clear()

    def clear(self) -> None:
        self.json_data = {}
        self.commit_to_disk()
