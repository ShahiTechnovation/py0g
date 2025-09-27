"""
Tests for we

Run with: python -m pytest tests/
"""

import pytest
from contracts.we import we


class Testwe:
    """Test suite for we contract."""
    
    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.owner = "0x1234567890123456789012345678901234567890"
        self.contract = we(self.owner)
    
    def test_initialization(self):
        """Test contract initialization."""
        assert self.contract.get_owner() == self.owner
        assert self.contract.get_counter() == 0
        assert len(self.contract.data) == 0
    
    def test_set_and_get_data(self):
        """Test data storage and retrieval."""
        # Test setting data
        result = self.contract.set_data("test_key", "test_value")
        assert result is True
        
        # Test getting data
        value = self.contract.get_data("test_key")
        assert value == "test_value"
        
        # Test non-existent key
        value = self.contract.get_data("nonexistent")
        assert value is None
    
    def test_counter_operations(self):
        """Test counter functionality."""
        # Initial counter value
        assert self.contract.get_counter() == 0
        
        # Increment counter
        new_value = self.contract.increment_counter()
        assert new_value == 1
        assert self.contract.get_counter() == 1
        
        # Increment again
        assert new_value == 2
        assert self.contract.get_counter() == 2
