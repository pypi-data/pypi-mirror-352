"""
localStoragePro - A familiar localStorage API from the Web, adapted for Python applications.

This package provides a simple, fast, and reliable local data storage with multiple backend options.
"""

__author__ = 'Suraj Mandal'
__copyright__ = 'Copyright (C) 2021-present Suraj Mandal'
__license__ = 'MIT License'
__version__ = '0.3.0'

from typing import Any, Dict, List, Optional

from .storage_backends import (
    BasicStorageBackend,
    TextStorageBackend,
    SQLiteStorageBackend,
    JSONStorageBackend
)

# Import async API components early to avoid circular imports
from .async_storage import AsyncLocalStoragePro, async_lsp

__all__ = ['localStoragePro', 'lsp', 'AsyncLocalStoragePro', 'async_lsp']


class localStoragePro:
    """
    A familiar API from the Web, adapted to storing data locally with Python.
    
    This class provides a localStorage-like interface for persisting key-value data
    using various storage backends (SQLite, JSON, or text files).
    
    Args:
        app_namespace (str): A unique identifier for your application (e.g., 'com.mycompany.myapp').
                           Must not contain path separators.
        storage_backend (str): Storage backend to use. Options: 'sqlite' (default), 'json', 'text'.
    """
    
    def __init__(self, app_namespace: str, storage_backend: str = "sqlite") -> None:
        self.storage_backend_instance = BasicStorageBackend(app_namespace)
        if storage_backend == "text":
            self.storage_backend_instance = TextStorageBackend(app_namespace)
        elif storage_backend == "sqlite":
            self.storage_backend_instance = SQLiteStorageBackend(app_namespace)
        elif storage_backend == "json":
            self.storage_backend_instance = JSONStorageBackend(app_namespace)
        else:
            self.storage_backend_instance = SQLiteStorageBackend(app_namespace)
        self.app_namespace = app_namespace
        self.storage_backend = storage_backend

    def getItem(self, item: str) -> Any:
        """Retrieve a value by its key."""
        return self.storage_backend_instance.get_item(item)

    def setItem(self, item: str, value: Any) -> None:
        """Store a value with the given key."""
        self.storage_backend_instance.set_item(item, value)

    def removeItem(self, item: str) -> None:
        """Remove a key-value pair."""
        self.storage_backend_instance.remove_item(item)

    def getAll(self) -> dict:
        """Retrieve all stored key-value pairs."""
        return self.storage_backend_instance.get_all()

    def getMany(self, items: list) -> dict:
        """Retrieve multiple values by their keys."""
        return self.storage_backend_instance.get_many(items)

    def removeAll(self) -> None:
        """Remove all stored key-value pairs."""
        self.storage_backend_instance.remove_all()

    def clear(self) -> None:
        """Clear all stored data (equivalent to removeAll)."""
        self.storage_backend_instance.clear()


# Singleton class for synchronous API
class LocalStorageProSingleton:
    """Singleton-like class for localStoragePro."""
    
    def __init__(self):
        self._instance = None
        self._namespace = None
        self._backend = None
    
    def __call__(self, app_namespace: str = None, storage_backend: str = None):
        """Create or update the instance with the given namespace and backend."""
        if app_namespace is not None:
            self._namespace = app_namespace
        if storage_backend is not None:
            self._backend = storage_backend
        
        if self._namespace is None:
            raise ValueError("No namespace provided for localStoragePro")
        
        backend = self._backend or "sqlite"
        self._instance = localStoragePro(self._namespace, backend)
        return self
    
    def getItem(self, item: str) -> Any:
        """Retrieve a value by its key."""
        self._ensure_initialized()
        return self._instance.getItem(item)
    
    def setItem(self, item: str, value: Any) -> None:
        """Store a value with the given key."""
        self._ensure_initialized()
        self._instance.setItem(item, value)
    
    def removeItem(self, item: str) -> None:
        """Remove a key-value pair."""
        self._ensure_initialized()
        self._instance.removeItem(item)
    
    def getAll(self) -> dict:
        """Retrieve all stored key-value pairs."""
        self._ensure_initialized()
        return self._instance.getAll()
    
    def getMany(self, items: list) -> dict:
        """Retrieve multiple values by their keys."""
        self._ensure_initialized()
        return self._instance.getMany(items)
    
    def removeAll(self) -> None:
        """Remove all stored key-value pairs."""
        self._ensure_initialized()
        self._instance.removeAll()
    
    def clear(self) -> None:
        """Clear all stored data (equivalent to removeAll)."""
        self._ensure_initialized()
        self._instance.clear()
    
    def _ensure_initialized(self):
        """Ensure the instance is initialized."""
        if self._instance is None:
            raise ValueError("localStoragePro not initialized. Call lsp('namespace') first.")


# Create singleton instance for synchronous API
lsp = LocalStorageProSingleton() 