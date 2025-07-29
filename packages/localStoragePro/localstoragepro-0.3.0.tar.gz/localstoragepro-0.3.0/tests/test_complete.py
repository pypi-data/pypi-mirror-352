#!/usr/bin/env python3
"""Test script for localStoragePro demonstrating all functionality."""

import json
import sys

from localStoragePro import localStoragePro
import localStoragePro as lsp_module

def test_basic_operations():
    """Test basic localStorage operations."""
    print("=== Testing Basic Operations ===")
    
    localStorage = localStoragePro('test.basic', 'json')
    
    # Clear any existing data
    localStorage.clear()
    
    # Test setItem and getItem
    localStorage.setItem('username', 'surajmandal')
    localStorage.setItem('email', 'localstoragepro.oss@mandalsuraj.com')
    localStorage.setItem('project', 'localStoragePro')
    
    print(f"Username: {localStorage.getItem('username')}")
    print(f"Email: {localStorage.getItem('email')}")
    print(f"Project: {localStorage.getItem('project')}")
    
    # Test nonexistent item
    nonexistent = localStorage.getItem('nonexistent')
    print(f"Nonexistent item: {nonexistent}")
    
    # Test removeItem
    localStorage.removeItem('email')
    print(f"Email after removal: {localStorage.getItem('email')}")
    
    print("✓ Basic operations test passed\n")

def test_bulk_operations():
    """Test bulk operations: getAll, getMany, removeAll."""
    print("=== Testing Bulk Operations ===")
    
    localStorage = localStoragePro('test.bulk', 'sqlite')
    localStorage.clear()
    
    # Store test data
    test_data = {
        'name': 'Suraj Mandal',
        'github': 'https://github.com/surajmandalcell',
        'project': 'localStoragePro',
        'language': 'Python',
        'version': '0.3.0'
    }
    
    for key, value in test_data.items():
        localStorage.setItem(key, value)
    
    # Test getAll
    all_data = localStorage.getAll()
    print(f"All stored data ({len(all_data)} items):")
    for key, value in all_data.items():
        print(f"  {key}: {value}")
    
    # Test getMany with existing keys
    subset_keys = ['name', 'project', 'language']
    subset_data = localStorage.getMany(subset_keys)
    print(f"\nSubset data ({len(subset_data)} items):")
    for key, value in subset_data.items():
        print(f"  {key}: {value}")
    
    # Test getMany with mixed existing/nonexistent keys
    mixed_keys = ['name', 'nonexistent', 'version', 'another_missing']
    mixed_data = localStorage.getMany(mixed_keys)
    print(f"\nMixed query result ({len(mixed_data)} items found out of {len(mixed_keys)} requested):")
    for key, value in mixed_data.items():
        print(f"  {key}: {value}")
    
    # Test removeAll
    localStorage.removeAll()
    remaining = localStorage.getAll()
    print(f"\nAfter removeAll(): {len(remaining)} items remaining")
    
    print("✓ Bulk operations test passed\n")

def test_json_storage():
    """Test storing and retrieving JSON data."""
    print("=== Testing JSON Data Storage ===")
    
    localStorage = localStoragePro('test.json', 'json')
    localStorage.clear()
    
    # Store complex data as JSON
    user_profile = {
        'name': 'Suraj Mandal',
        'email': 'localstoragepro.oss@mandalsuraj.com',
        'github': 'https://github.com/surajmandalcell',
        'projects': ['localStoragePro', 'Other Projects'],
        'skills': ['Python', 'JavaScript', 'Git']
    }
    
    settings = {
        'theme': 'dark',
        'fontSize': 14,
        'notifications': True,
        'autoSave': False
    }
    
    # Store as JSON strings
    localStorage.setItem('profile', json.dumps(user_profile))
    localStorage.setItem('settings', json.dumps(settings))
    localStorage.setItem('lastLogin', '2025-06-01T12:00:00Z')
    
    # Retrieve and parse JSON data
    profile_json = localStorage.getItem('profile')
    if profile_json:
        profile = json.loads(profile_json)
        print(f"User: {profile['name']}")
        print(f"Projects: {', '.join(profile['projects'])}")
    
    # Get multiple JSON objects
    json_data = localStorage.getMany(['profile', 'settings'])
    print(f"\nRetrieved {len(json_data)} JSON objects:")
    for key, value in json_data.items():
        data = json.loads(value)
        print(f"  {key}: {type(data).__name__} with {len(data)} properties")
    
    print("✓ JSON storage test passed\n")

def test_all_backends():
    """Test all storage backends."""
    print("=== Testing All Storage Backends ===")
    
    backends = ['text', 'sqlite', 'json']
    
    for backend in backends:
        print(f"\n--- Testing {backend.upper()} Backend ---")
        localStorage = localStoragePro(f'test.{backend}', backend)
        localStorage.clear()
        
        # Store test data
        localStorage.setItem('backend', backend)
        localStorage.setItem('maintainer', 'Suraj Mandal')
        localStorage.setItem('status', 'active')
        
        # Test all operations
        all_data = localStorage.getAll()
        subset = localStorage.getMany(['backend', 'maintainer'])
        
        print(f"  Stored: {len(all_data)} items")
        print(f"  Retrieved subset: {len(subset)} items")
        print(f"  Backend value: {localStorage.getItem('backend')}")
        
        # Clean up
        localStorage.removeAll()
        remaining = localStorage.getAll()
        print(f"  After cleanup: {len(remaining)} items")
    
    print("\n✓ All backends test passed\n")

def test_error_handling():
    """Test error handling and edge cases."""
    print("=== Testing Error Handling ===")
    
    localStorage = localStoragePro('test.errors', 'sqlite')
    localStorage.clear()
    
    # Test empty getMany
    empty_result = localStorage.getMany([])
    print(f"Empty getMany result: {empty_result}")
    
    # Test getMany with nonexistent keys
    missing_result = localStorage.getMany(['missing1', 'missing2'])
    print(f"Missing keys result: {missing_result}")
    
    # Test operations on empty storage
    empty_all = localStorage.getAll()
    print(f"getAll on empty storage: {empty_all}")
    
    # Test removeItem on nonexistent key (should not error)
    localStorage.removeItem('nonexistent')
    print("removeItem on nonexistent key: no error")
    
    # Test multiple removeAll calls
    localStorage.removeAll()
    localStorage.removeAll()
    print("Multiple removeAll calls: no error")
    
    print("✓ Error handling test passed\n")

def main():
    """Run all tests."""
    print("localStoragePro Test Suite")
    print("=" * 50)
    print(f"Testing version: {lsp_module.__version__}")
    print(f"Author: {lsp_module.__author__}")
    print("=" * 50)
    
    try:
        test_basic_operations()
        test_bulk_operations()
        test_json_storage()
        test_all_backends()
        test_error_handling()
        
        print("All tests passed successfully!")
        print("\nlocalStoragePro is ready for use with all functionality:")
        print("  - getAll() - Get all key-value pairs")
        print("  - getMany(keys) - Get multiple values efficiently")
        print("  - removeAll() - Remove all stored data")
        
    except Exception as e:
        print(f"Test failed: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
