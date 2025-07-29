"""Test suite for localStoragePro."""

import json
import pytest
from localStoragePro import localStoragePro

class TestBasicOperations:
    """Test basic localStorage operations."""

    def test_set_and_get_item(self):
        """Test setItem and getItem functionality."""
        storage = localStoragePro('test.basic', 'json')
        storage.clear()

        storage.setItem('username', 'surajmandal')
        storage.setItem('email', 'localstoragepro.oss@mandalsuraj.com')

        assert storage.getItem('username') == 'surajmandal'
        assert storage.getItem('email') == 'localstoragepro.oss@mandalsuraj.com'
        assert storage.getItem('nonexistent') is None

    def test_remove_item(self):
        """Test removeItem functionality."""
        storage = localStoragePro('test.remove', 'json')
        storage.clear()

        storage.setItem('test_key', 'test_value')
        assert storage.getItem('test_key') == 'test_value'

        storage.removeItem('test_key')
        assert storage.getItem('test_key') is None

        # Removing non-existent key should not raise error
        storage.removeItem('nonexistent')

    def test_clear_storage(self):
        """Test clear functionality."""
        storage = localStoragePro('test.clear', 'json')

        storage.setItem('key1', 'value1')
        storage.setItem('key2', 'value2')

        storage.clear()
        assert len(storage.getAll()) == 0


class TestBulkOperations:
    """Test bulk operations functionality."""

    def test_get_all(self):
        """Test getAll functionality."""
        storage = localStoragePro('test.getall', 'sqlite')
        storage.clear()

        test_data = {
            'name': 'Suraj Mandal',
            'project': 'localStoragePro',
            'language': 'Python'
        }

        for key, value in test_data.items():
            storage.setItem(key, value)

        all_data = storage.getAll()
        assert len(all_data) == 3
        assert all_data == test_data

    def test_get_many(self):
        """Test getMany functionality."""
        storage = localStoragePro('test.getmany', 'sqlite')
        storage.clear()

        # Setup test data
        storage.setItem('key1', 'value1')
        storage.setItem('key2', 'value2')
        storage.setItem('key3', 'value3')

        # Test getting existing keys
        result = storage.getMany(['key1', 'key3'])
        expected = {'key1': 'value1', 'key3': 'value3'}
        assert result == expected

        # Test mixed existing/non-existing keys
        result = storage.getMany(['key1', 'nonexistent', 'key2'])
        expected = {'key1': 'value1', 'key2': 'value2'}
        assert result == expected

        # Test empty list
        result = storage.getMany([])
        assert result == {}

    def test_remove_all(self):
        """Test removeAll functionality."""
        storage = localStoragePro('test.removeall', 'sqlite')

        # Add some data
        storage.setItem('key1', 'value1')
        storage.setItem('key2', 'value2')

        # Verify data exists
        assert len(storage.getAll()) == 2

        # Remove all
        storage.removeAll()
        assert len(storage.getAll()) == 0


class TestStorageBackends:
    """Test all storage backends."""

    @pytest.mark.parametrize("backend", ['text', 'sqlite', 'json'])
    def test_backend_consistency(self, backend):
        """Test that all backends work consistently."""
        storage = localStoragePro(f'test.backend.{backend}', backend)
        storage.clear()

        # Test basic operations
        storage.setItem('test_key', 'test_value')
        assert storage.getItem('test_key') == 'test_value'

        # Test bulk operations
        test_data = {'key1': 'value1', 'key2': 'value2', 'key3': 'value3'}
        for key, value in test_data.items():
            storage.setItem(key, value)

        all_data = storage.getAll()
        assert len(all_data) == 4  # Including test_key

        subset = storage.getMany(['key1', 'key3'])
        assert subset == {'key1': 'value1', 'key3': 'value3'}

        storage.removeAll()
        assert len(storage.getAll()) == 0


class TestErrorHandling:
    """Test error handling scenarios."""

    def test_invalid_namespace(self):
        """Test that invalid namespaces raise appropriate errors."""
        # Test with backslash (Windows path separator)
        with pytest.raises(Exception):
            localStoragePro('invalid\\namespace', 'json')

    def test_nonexistent_operations(self):
        """Test operations on non-existent keys."""
        storage = localStoragePro('test.errors', 'json')
        storage.clear()

        # Getting non-existent key should return None
        assert storage.getItem('nonexistent') is None

        # Getting many with non-existent keys should return empty dict
        result = storage.getMany(['nonexistent1', 'nonexistent2'])
        assert result == {}

        # Removing non-existent key should not raise error
        storage.removeItem('nonexistent')


class TestJSONDataHandling:
    """Test handling of JSON data."""

    def test_json_storage_and_retrieval(self):
        """Test storing and retrieving JSON data."""
        storage = localStoragePro('test.json', 'json')
        storage.clear()

        # Store complex JSON data
        user_data = {
            "name": "Suraj Mandal",
            "settings": {"theme": "dark", "notifications": True},
            "projects": ["localStoragePro", "Other"]
        }

        storage.setItem('user_profile', json.dumps(user_data))

        # Retrieve and verify
        retrieved = json.loads(storage.getItem('user_profile'))
        assert retrieved == user_data
        assert retrieved['name'] == 'Suraj Mandal'
        assert retrieved['settings']['theme'] == 'dark'
        assert len(retrieved['projects']) == 2
