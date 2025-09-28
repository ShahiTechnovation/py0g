"""
Simple test contract to verify EVM stack fixes.
"""

class SimpleTest:
    """A minimal contract to test EVM function calls."""
    
    def __init__(self, owner: str):
        """Initialize with owner."""
        self.owner = owner
        self.value = 42
    
    def get_owner(self) -> str:
        """Return the owner address."""
        return self.owner
    
    def get_value(self) -> int:
        """Return a simple value."""
        return self.value
