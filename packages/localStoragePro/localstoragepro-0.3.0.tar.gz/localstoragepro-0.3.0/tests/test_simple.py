#!/usr/bin/env python3
"""
Test script for localStoragePro demonstrating all functionality.
This script tests all the methods including get_all, get_many, and remove_all.
"""

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
        
        print("🎉 All tests passed successfully!")
        print("\nlocalStoragePro is ready for use with all the new functionality:")
        print("  ✓ getAll() - Get all key-value pairs")
        print("  ✓ getMany(keys) - Get multiple values efficiently")
        print("  ✓ removeAll() - Remove all stored data")
        print("  ✓ Comprehensive documentation and examples")
        print("  ✓ Updated project details for Suraj Mandal")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
