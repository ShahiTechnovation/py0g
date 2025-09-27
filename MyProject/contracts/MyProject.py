"""
MyProject - A basic Python smart contract

A smart contract for MyProject
"""

from typing import Dict, Any


class MyProject:
    """
    A basic smart contract written in Python.
    
    This contract demonstrates the fundamental patterns for
    writing smart contracts in Python for 0G Galileo.
    """
    
    def __init__(self, owner: str):
        """
        Initialize the contract.
        
        Args:
            owner: Address of the contract owner
        """
        self.owner: str = owner
        self.data: Dict[str, Any] = {}
        self.counter: int = 0
    
    def set_data(self, key: str, value: Any) -> bool:
        """
        Store data in the contract.
        
        Args:
            key: The key to store data under
            value: The value to store
            
        Returns:
            bool: True if successful
        """
        self.data[key] = value
        return True
    
    def get_data(self, key: str) -> Any:
        """
        Retrieve data from the contract.
        
        Args:
            key: The key to retrieve data for
            
        Returns:
            Any: The stored value or None if not found
        """
        return self.data.get(key)
    
    def increment_counter(self) -> int:
        """
        Increment the counter.
        
        Returns:
            int: The new counter value
        """
        self.counter += 1
        return self.counter
    
    def get_counter(self) -> int:
        """
        Get the current counter value.
        
        Returns:
            int: Current counter value
        """
        return self.counter
    
    def get_owner(self) -> str:
        """
        Get the contract owner.
        
        Returns:
            str: Owner address
        """
        return self.owner
