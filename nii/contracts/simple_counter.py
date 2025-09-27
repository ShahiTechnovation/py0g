"""
Simple Counter Contract for Testing

A minimal contract to demonstrate py0g functionality.
"""

class SimpleCounter:
    """A simple counter contract."""
    
    def __init__(self, owner: str):
        """Initialize counter."""
        self.owner: str = owner
        self.count: int = 0
        self.name: str = "SimpleCounter"
    
    def get_count(self) -> int:
        """Get current count (read-only)."""
        return self.count
    
    def get_owner(self) -> str:
        """Get contract owner (read-only)."""
        return self.owner
    
    def get_name(self) -> str:
        """Get contract name (read-only)."""
        return self.name
    
    def increment(self, caller: str) -> bool:
        """Increment counter (write operation)."""
        if caller == self.owner:
            self.count += 1
            return True
        return False
    
    def set_count(self, caller: str, new_count: int) -> bool:
        """Set counter value (write operation)."""
        if caller == self.owner:
            self.count = new_count
            return True
        return False
