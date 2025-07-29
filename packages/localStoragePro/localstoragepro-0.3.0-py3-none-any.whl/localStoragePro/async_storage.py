"""Async wrapper for localStoragePro."""

import asyncio
from typing import Any, Dict, List, Optional
import sys
import traceback

from .storage_backends import BasicStorageBackend, TextStorageBackend, SQLiteStorageBackend, JSONStorageBackend


class AsyncStorageBackend:
    """Async wrapper for storage backends."""
    
    def __init__(self, backend: BasicStorageBackend, app_namespace: str):
        self.backend = backend
        self.app_namespace = app_namespace
        self.backend_type = type(backend).__name__
    
    async def get_item(self, item: str) -> Optional[str]:
        """Get item asynchronously."""
        try:
            return await asyncio.to_thread(self._execute_operation, "get_item", item)
        except Exception as e:
            print(f"Error in get_item: {e}")
            traceback.print_exc()
            return None
    
    async def set_item(self, item: str, value: Any) -> None:
        """Set item asynchronously."""
        try:
            await asyncio.to_thread(self._execute_operation, "set_item", item, value)
        except Exception as e:
            print(f"Error in set_item: {e}")
            traceback.print_exc()
    
    async def remove_item(self, item: str) -> None:
        """Remove item asynchronously."""
        try:
            await asyncio.to_thread(self._execute_operation, "remove_item", item)
        except Exception as e:
            print(f"Error in remove_item: {e}")
            traceback.print_exc()
    
    async def get_all(self) -> Dict[str, str]:
        """Get all items asynchronously."""
        try:
            return await asyncio.to_thread(self._execute_operation, "get_all")
        except Exception as e:
            print(f"Error in get_all: {e}")
            traceback.print_exc()
            return {}
    
    async def get_many(self, items: List[str]) -> Dict[str, str]:
        """Get many items asynchronously."""
        try:
            return await asyncio.to_thread(self._execute_operation, "get_many", items)
        except Exception as e:
            print(f"Error in get_many: {e}")
            traceback.print_exc()
            return {}
    
    async def remove_all(self) -> None:
        """Remove all items asynchronously."""
        try:
            await asyncio.to_thread(self._execute_operation, "remove_all")
        except Exception as e:
            print(f"Error in remove_all: {e}")
            traceback.print_exc()
    
    async def clear(self) -> None:
        """Clear storage asynchronously."""
        try:
            await asyncio.to_thread(self._execute_operation, "clear")
        except Exception as e:
            print(f"Error in clear: {e}")
            traceback.print_exc()
    
    def _execute_operation(self, operation: str, *args) -> Any:
        """Execute operation in a thread-safe manner by recreating backend if needed."""
        try:
            # For SQLite, we need to create a new connection in each thread
            if self.backend_type == "SQLiteStorageBackend":
                backend = SQLiteStorageBackend(self.app_namespace)
            elif self.backend_type == "JSONStorageBackend":
                backend = JSONStorageBackend(self.app_namespace)
            elif self.backend_type == "TextStorageBackend":
                backend = TextStorageBackend(self.app_namespace)
            else:
                backend = BasicStorageBackend(self.app_namespace)
            
            # Execute the requested operation
            if operation == "get_item":
                return backend.get_item(*args)
            elif operation == "set_item":
                return backend.set_item(*args)
            elif operation == "remove_item":
                return backend.remove_item(*args)
            elif operation == "get_all":
                return backend.get_all()
            elif operation == "get_many":
                return backend.get_many(*args)
            elif operation == "remove_all":
                return backend.remove_all()
            elif operation == "clear":
                return backend.clear()
        except Exception as e:
            print(f"Error in _execute_operation ({operation}): {e}")
            traceback.print_exc()
            if operation == "get_item":
                return None
            elif operation in ("get_all", "get_many"):
                return {}
            return None


class AsyncLocalStoragePro:
    """Async version of localStoragePro."""
    
    def __init__(self, app_namespace: str, storage_backend: str = "sqlite") -> None:
        """Initialize AsyncLocalStoragePro with the specified namespace and backend."""
        try:
            backend = BasicStorageBackend(app_namespace)
            if storage_backend == "text":
                backend = TextStorageBackend(app_namespace)
            elif storage_backend == "sqlite":
                backend = SQLiteStorageBackend(app_namespace)
            elif storage_backend == "json":
                backend = JSONStorageBackend(app_namespace)
            else:
                backend = SQLiteStorageBackend(app_namespace)
            
            self.storage_backend_instance = AsyncStorageBackend(backend, app_namespace)
            self.app_namespace = app_namespace
            self.storage_backend = storage_backend
        except Exception as e:
            print(f"Error in AsyncLocalStoragePro.__init__: {e}")
            traceback.print_exc()
    
    async def getItem(self, item: str) -> Any:
        """Retrieve a value by its key asynchronously."""
        try:
            return await self.storage_backend_instance.get_item(item)
        except Exception as e:
            print(f"Error in getItem: {e}")
            traceback.print_exc()
            return None
    
    async def setItem(self, item: str, value: Any) -> None:
        """Store a value with the given key asynchronously."""
        try:
            await self.storage_backend_instance.set_item(item, value)
        except Exception as e:
            print(f"Error in setItem: {e}")
            traceback.print_exc()
    
    async def removeItem(self, item: str) -> None:
        """Remove a key-value pair asynchronously."""
        try:
            await self.storage_backend_instance.remove_item(item)
        except Exception as e:
            print(f"Error in removeItem: {e}")
            traceback.print_exc()
    
    async def getAll(self) -> dict:
        """Retrieve all stored key-value pairs asynchronously."""
        try:
            return await self.storage_backend_instance.get_all()
        except Exception as e:
            print(f"Error in getAll: {e}")
            traceback.print_exc()
            return {}
    
    async def getMany(self, items: list) -> dict:
        """Retrieve multiple values by their keys asynchronously."""
        try:
            return await self.storage_backend_instance.get_many(items)
        except Exception as e:
            print(f"Error in getMany: {e}")
            traceback.print_exc()
            return {}
    
    async def removeAll(self) -> None:
        """Remove all stored key-value pairs asynchronously."""
        try:
            await self.storage_backend_instance.remove_all()
        except Exception as e:
            print(f"Error in removeAll: {e}")
            traceback.print_exc()
    
    async def clear(self) -> None:
        """Clear all stored data asynchronously (equivalent to removeAll)."""
        try:
            await self.storage_backend_instance.clear()
        except Exception as e:
            print(f"Error in clear: {e}")
            traceback.print_exc()


class AsyncLocalStorageProSingleton:
    """Singleton-like class for AsyncLocalStoragePro."""
    
    def __init__(self):
        self._instance = None
        self._namespace = None
        self._backend = None
    
    def __call__(self, app_namespace: str = None, storage_backend: str = None):
        """Create or update the instance with the given namespace and backend."""
        try:
            if app_namespace is not None:
                self._namespace = app_namespace
            if storage_backend is not None:
                self._backend = storage_backend
            
            if self._namespace is None:
                raise ValueError("No namespace provided for AsyncLocalStoragePro")
            
            backend = self._backend or "sqlite"
            self._instance = AsyncLocalStoragePro(self._namespace, backend)
            return self
        except Exception as e:
            print(f"Error in AsyncLocalStorageProSingleton.__call__: {e}")
            traceback.print_exc()
            return self
    
    async def getItem(self, item: str) -> Any:
        """Retrieve a value by its key asynchronously."""
        try:
            self._ensure_initialized()
            return await self._instance.getItem(item)
        except Exception as e:
            print(f"Error in async_lsp.getItem: {e}")
            traceback.print_exc()
            return None
    
    async def setItem(self, item: str, value: Any) -> None:
        """Store a value with the given key asynchronously."""
        try:
            self._ensure_initialized()
            await self._instance.setItem(item, value)
        except Exception as e:
            print(f"Error in async_lsp.setItem: {e}")
            traceback.print_exc()
    
    async def removeItem(self, item: str) -> None:
        """Remove a key-value pair asynchronously."""
        try:
            self._ensure_initialized()
            await self._instance.removeItem(item)
        except Exception as e:
            print(f"Error in async_lsp.removeItem: {e}")
            traceback.print_exc()
    
    async def getAll(self) -> dict:
        """Retrieve all stored key-value pairs asynchronously."""
        try:
            self._ensure_initialized()
            return await self._instance.getAll()
        except Exception as e:
            print(f"Error in async_lsp.getAll: {e}")
            traceback.print_exc()
            return {}
    
    async def getMany(self, items: list) -> dict:
        """Retrieve multiple values by their keys asynchronously."""
        try:
            self._ensure_initialized()
            return await self._instance.getMany(items)
        except Exception as e:
            print(f"Error in async_lsp.getMany: {e}")
            traceback.print_exc()
            return {}
    
    async def removeAll(self) -> None:
        """Remove all stored key-value pairs asynchronously."""
        try:
            self._ensure_initialized()
            await self._instance.removeAll()
        except Exception as e:
            print(f"Error in async_lsp.removeAll: {e}")
            traceback.print_exc()
    
    async def clear(self) -> None:
        """Clear all stored data asynchronously (equivalent to removeAll)."""
        try:
            self._ensure_initialized()
            await self._instance.clear()
        except Exception as e:
            print(f"Error in async_lsp.clear: {e}")
            traceback.print_exc()
    
    def _ensure_initialized(self):
        """Ensure the instance is initialized."""
        if self._instance is None:
            raise ValueError("AsyncLocalStoragePro not initialized. Call async_lsp('namespace') first.")


# Create a singleton instance
async_lsp = AsyncLocalStorageProSingleton() 