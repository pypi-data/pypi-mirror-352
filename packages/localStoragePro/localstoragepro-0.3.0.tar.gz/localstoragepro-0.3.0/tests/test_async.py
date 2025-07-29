"""Tests for async version of localStoragePro."""

import asyncio
import json
import pytest
from localStoragePro import async_lsp, AsyncLocalStoragePro


@pytest.mark.asyncio
async def test_basic_async_operations():
    """Test basic async operations."""
    storage = AsyncLocalStoragePro('test.async.basic', 'sqlite')
    await storage.clear()
    
    # Test set and get
    await storage.setItem('username', 'surajmandal')
    await storage.setItem('email', 'localstoragepro.oss@mandalsuraj.com')
    
    assert await storage.getItem('username') == 'surajmandal'
    assert await storage.getItem('email') == 'localstoragepro.oss@mandalsuraj.com'
    assert await storage.getItem('nonexistent') is None
    
    # Test remove
    await storage.removeItem('username')
    assert await storage.getItem('username') is None
    
    # Clean up
    await storage.clear()


@pytest.mark.asyncio
async def test_async_bulk_operations():
    """Test async bulk operations."""
    storage = AsyncLocalStoragePro('test.async.bulk', 'json')
    await storage.clear()
    
    # Store test data
    test_data = {
        'name': 'Suraj Mandal',
        'project': 'localStoragePro',
        'language': 'Python'
    }
    
    # Store data concurrently
    tasks = []
    for key, value in test_data.items():
        tasks.append(storage.setItem(key, value))
    await asyncio.gather(*tasks)
    
    # Test getAll
    all_data = await storage.getAll()
    assert len(all_data) == len(test_data)
    assert all_data == test_data
    
    # Test getMany
    subset = await storage.getMany(['name', 'language'])
    assert subset == {'name': 'Suraj Mandal', 'language': 'Python'}
    
    # Test getMany with nonexistent keys
    mixed = await storage.getMany(['name', 'nonexistent', 'language'])
    assert mixed == {'name': 'Suraj Mandal', 'language': 'Python'}
    
    # Test removeAll
    await storage.removeAll()
    assert len(await storage.getAll()) == 0


@pytest.mark.asyncio
async def test_async_singleton():
    """Test the async singleton instance."""
    await async_lsp('test.async.singleton', 'sqlite').clear()
    
    # Set and get
    await async_lsp.setItem('key1', 'value1')
    assert await async_lsp.getItem('key1') == 'value1'
    
    # Test getAll
    all_data = await async_lsp.getAll()
    assert len(all_data) == 1
    assert all_data['key1'] == 'value1'
    
    # Test removeItem
    await async_lsp.removeItem('key1')
    assert await async_lsp.getItem('key1') is None
    
    # Clean up
    await async_lsp.clear()


@pytest.mark.asyncio
async def test_async_backends():
    """Test async operations with different backends."""
    backends = ['text', 'sqlite', 'json']
    
    for backend in backends:
        storage = AsyncLocalStoragePro(f'test.async.backend.{backend}', backend)
        await storage.clear()
        
        # Test basic operations
        await storage.setItem('test_key', 'test_value')
        assert await storage.getItem('test_key') == 'test_value'
        
        # Test bulk operations
        test_data = {'key1': 'value1', 'key2': 'value2', 'key3': 'value3'}
        for key, value in test_data.items():
            await storage.setItem(key, value)
        
        all_data = await storage.getAll()
        assert len(all_data) == 4  # Including test_key
        
        # Clean up
        await storage.clear()


@pytest.mark.asyncio
async def test_async_json_data():
    """Test storing and retrieving JSON data asynchronously."""
    storage = AsyncLocalStoragePro('test.async.json', 'json')
    await storage.clear()
    
    # Store complex data as JSON
    user_data = {
        "name": "Suraj Mandal",
        "settings": {"theme": "dark", "notifications": True},
        "projects": ["localStoragePro", "Other"]
    }
    
    await storage.setItem('user_profile', json.dumps(user_data))
    
    # Retrieve and verify
    retrieved = json.loads(await storage.getItem('user_profile'))
    assert retrieved == user_data
    assert retrieved['name'] == 'Suraj Mandal'
    assert retrieved['settings']['theme'] == 'dark'
    
    # Clean up
    await storage.clear()


@pytest.mark.asyncio
async def test_async_concurrent_operations():
    """Test concurrent async operations."""
    storage = AsyncLocalStoragePro('test.async.concurrent', 'sqlite')
    await storage.clear()
    
    # Generate test data
    test_keys = [f"key_{i}" for i in range(5)]
    test_values = [f"value_{i}" for i in range(5)]
    
    # Store data concurrently
    store_tasks = []
    for key, value in zip(test_keys, test_values):
        store_tasks.append(storage.setItem(key, value))
    await asyncio.gather(*store_tasks)
    
    # Retrieve data concurrently
    get_tasks = []
    for key in test_keys:
        get_tasks.append(storage.getItem(key))
    results = await asyncio.gather(*get_tasks)
    
    # Verify results
    assert results == test_values
    
    # Clean up
    await storage.clear() 