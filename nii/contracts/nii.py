"""
SEY Token - A basic fungible token in Python

This contract demonstrates how to implement a simple
fungible token (similar to ERC-20) for 0G Galileo.
"""

from typing import Dict


class SEYToken:
    """
    A basic token smart contract written in Python.
    
    Token Name: SEY Token
    Symbol: SEY
    Decimals: 18
    """
    
    def __init__(self, owner: str, initial_supply: int):
        """
        Initialize the token contract.
        
        Args:
            owner: The address of the contract owner
            initial_supply: The total supply of tokens
        """
        self.name: str = "SEY Token"
        self.symbol: str = "SEY"
        self.decimals: int = 18
        self.total_supply: int = initial_supply
        
        self.owner: str = owner
        self.balances: Dict[str, int] = {owner: initial_supply}
        self.allowances: Dict[str, Dict[str, int]] = {}
    
    def balance_of(self, account: str) -> int:
        """
        Get the balance of an account.
        
        Args:
            account: The address to check
            
        Returns:
            int: Token balance of the account
        """
        return self.balances.get(account, 0)
    
    def transfer(self, sender: str, recipient: str, amount: int) -> bool:
        """
        Transfer tokens from sender to recipient.
        
        Args:
            sender: The address of the sender
            recipient: The address of the recipient
            amount: The amount of tokens to transfer
            
        Returns:
            bool: True if successful
        """
        if amount <= 0 or self.balance_of(sender) < amount:
            return False
        
        # Deduct from sender
        self.balances[sender] -= amount
        # Add to recipient
        self.balances[recipient] = self.balance_of(recipient) + amount
        return True
    
    def approve(self, owner: str, spender: str, amount: int) -> bool:
        """
        Approve a spender to spend tokens on behalf of the owner.
        
        Args:
            owner: The token owner
            spender: The address allowed to spend
            amount: The amount approved
            
        Returns:
            bool: True if successful
        """
        if owner not in self.allowances:
            self.allowances[owner] = {}
        
        self.allowances[owner][spender] = amount
        return True
    
    def allowance(self, owner: str, spender: str) -> int:
        """
        Get the remaining allowance for a spender.
        
        Args:
            owner: The token owner
            spender: The approved spender
            
        Returns:
            int: Remaining allowance
        """
        return self.allowances.get(owner, {}).get(spender, 0)
    
    def transfer_from(self, spender: str, sender: str, recipient: str, amount: int) -> bool:
        """
        Transfer tokens on behalf of another account.
        
        Args:
            spender: The address executing the transfer
            sender: The address tokens are sent from
            recipient: The address tokens are sent to
            amount: The amount of tokens to transfer
            
        Returns:
            bool: True if successful
        """
        allowed = self.allowance(sender, spender)
        
        if amount <= 0 or self.balance_of(sender) < amount or allowed < amount:
            return False
        
        # Deduct from sender balance
        self.balances[sender] -= amount
        # Add to recipient balance
        self.balances[recipient] = self.balance_of(recipient) + amount
        # Reduce allowance
        self.allowances[sender][spender] -= amount
        
        return True
