"""
STRK Token - Advanced Python Token Contract

This contract demonstrates advanced token functionality including:
- Minting and burning
- Transfer with allowances
- Owner controls
- Event logging simulation
"""

from typing import Dict, List, Optional


class STRKToken:
    """
    STRK Token - A comprehensive ERC-20 style token in Python.
    
    Token Name: STRK Token
    Symbol: STRK
    Decimals: 18
    Features: Mintable, Burnable, Ownable
    """
    
    def __init__(self, owner: str, initial_supply: int = 1000000):
        """
        Initialize the STRK token contract.
        
        Args:
            owner: The address of the contract owner
            initial_supply: Initial token supply (default: 1M tokens)
        """
        # Token metadata
        self.name: str = "STRK Token"
        self.symbol: str = "STRK"
        self.decimals: int = 18
        self.total_supply: int = initial_supply * (10 ** self.decimals)
        
        # Access control
        self.owner: str = owner
        self.minters: Dict[str, bool] = {owner: True}
        
        # Token state
        self.balances: Dict[str, int] = {owner: self.total_supply}
        self.allowances: Dict[str, Dict[str, int]] = {}
        
        # Event logs (simulated)
        self.events: List[Dict] = []
        
        # Emit Transfer event for initial supply
        self._emit_transfer("0x0000000000000000000000000000000000000000", owner, self.total_supply)
    
    def balance_of(self, account: str) -> int:
        """
        Get the token balance of an account.
        
        Args:
            account: The address to check
            
        Returns:
            int: Token balance in wei (smallest unit)
        """
        return self.balances.get(account, 0)
    
    def transfer(self, sender: str, recipient: str, amount: int) -> bool:
        """
        Transfer tokens from sender to recipient.
        
        Args:
            sender: The address of the sender
            recipient: The address of the recipient
            amount: The amount of tokens to transfer (in wei)
            
        Returns:
            bool: True if successful, False otherwise
        """
        if amount <= 0:
            return False
            
        if self.balance_of(sender) < amount:
            return False
        
        if sender == recipient:
            return False
        
        # Perform transfer
        self.balances[sender] -= amount
        self.balances[recipient] = self.balance_of(recipient) + amount
        
        # Emit Transfer event
        self._emit_transfer(sender, recipient, amount)
        
        return True
    
    def approve(self, owner: str, spender: str, amount: int) -> bool:
        """
        Approve a spender to spend tokens on behalf of the owner.
        
        Args:
            owner: The token owner
            spender: The address allowed to spend
            amount: The amount approved (in wei)
            
        Returns:
            bool: True if successful
        """
        if owner not in self.allowances:
            self.allowances[owner] = {}
        
        self.allowances[owner][spender] = amount
        
        # Emit Approval event
        self._emit_approval(owner, spender, amount)
        
        return True
    
    def allowance(self, owner: str, spender: str) -> int:
        """
        Get the remaining allowance for a spender.
        
        Args:
            owner: The token owner
            spender: The approved spender
            
        Returns:
            int: Remaining allowance in wei
        """
        return self.allowances.get(owner, {}).get(spender, 0)
    
    def transfer_from(self, spender: str, sender: str, recipient: str, amount: int) -> bool:
        """
        Transfer tokens on behalf of another account using allowance.
        
        Args:
            spender: The address executing the transfer
            sender: The address tokens are sent from
            recipient: The address tokens are sent to
            amount: The amount of tokens to transfer (in wei)
            
        Returns:
            bool: True if successful
        """
        if amount <= 0:
            return False
            
        current_allowance = self.allowance(sender, spender)
        
        if current_allowance < amount:
            return False
        
        if self.balance_of(sender) < amount:
            return False
        
        # Perform transfer
        if self.transfer(sender, recipient, amount):
            # Reduce allowance
            self.allowances[sender][spender] = current_allowance - amount
            return True
        
        return False
    
    def mint(self, caller: str, to: str, amount: int) -> bool:
        """
        Mint new tokens to an address (only authorized minters).
        
        Args:
            caller: Address calling this function
            to: Address to mint tokens to
            amount: Amount to mint (in wei)
            
        Returns:
            bool: True if successful
        """
        # Check if caller is authorized to mint
        if not self.minters.get(caller, False):
            return False
        
        if amount <= 0:
            return False
        
        # Mint tokens
        self.total_supply += amount
        self.balances[to] = self.balance_of(to) + amount
        
        # Emit Transfer event (from zero address)
        self._emit_transfer("0x0000000000000000000000000000000000000000", to, amount)
        
        return True
    
    def burn(self, caller: str, amount: int) -> bool:
        """
        Burn tokens from caller's balance.
        
        Args:
            caller: Address calling this function
            amount: Amount to burn (in wei)
            
        Returns:
            bool: True if successful
        """
        if amount <= 0:
            return False
            
        if self.balance_of(caller) < amount:
            return False
        
        # Burn tokens
        self.balances[caller] -= amount
        self.total_supply -= amount
        
        # Emit Transfer event (to zero address)
        self._emit_transfer(caller, "0x0000000000000000000000000000000000000000", amount)
        
        return True
    
    def burn_from(self, caller: str, account: str, amount: int) -> bool:
        """
        Burn tokens from another account using allowance.
        
        Args:
            caller: Address calling this function
            account: Account to burn tokens from
            amount: Amount to burn (in wei)
            
        Returns:
            bool: True if successful
        """
        if amount <= 0:
            return False
            
        current_allowance = self.allowance(account, caller)
        
        if current_allowance < amount:
            return False
        
        if self.balance_of(account) < amount:
            return False
        
        # Burn tokens
        self.balances[account] -= amount
        self.total_supply -= amount
        
        # Reduce allowance
        self.allowances[account][caller] = current_allowance - amount
        
        # Emit Transfer event (to zero address)
        self._emit_transfer(account, "0x0000000000000000000000000000000000000000", amount)
        
        return True
    
    def add_minter(self, caller: str, minter: str) -> bool:
        """
        Add a new minter (only owner).
        
        Args:
            caller: Address calling this function
            minter: Address to grant minting rights
            
        Returns:
            bool: True if successful
        """
        if caller != self.owner:
            return False
        
        self.minters[minter] = True
        return True
    
    def remove_minter(self, caller: str, minter: str) -> bool:
        """
        Remove a minter (only owner).
        
        Args:
            caller: Address calling this function
            minter: Address to revoke minting rights
            
        Returns:
            bool: True if successful
        """
        if caller != self.owner:
            return False
        
        if minter == self.owner:
            return False  # Owner cannot remove themselves
        
        self.minters[minter] = False
        return True
    
    def is_minter(self, account: str) -> bool:
        """
        Check if an account has minting rights.
        
        Args:
            account: Address to check
            
        Returns:
            bool: True if account is a minter
        """
        return self.minters.get(account, False)
    
    def transfer_ownership(self, caller: str, new_owner: str) -> bool:
        """
        Transfer contract ownership (only current owner).
        
        Args:
            caller: Address calling this function
            new_owner: New owner address
            
        Returns:
            bool: True if successful
        """
        if caller != self.owner:
            return False
        
        if new_owner == "0x0000000000000000000000000000000000000000":
            return False  # Cannot transfer to zero address
        
        old_owner = self.owner
        self.owner = new_owner
        
        # New owner becomes a minter, old owner loses minting rights
        self.minters[new_owner] = True
        if old_owner != new_owner:
            self.minters[old_owner] = False
        
        return True
    
    def get_events(self, event_type: Optional[str] = None) -> List[Dict]:
        """
        Get contract events (for debugging/monitoring).
        
        Args:
            event_type: Filter by event type (Transfer, Approval)
            
        Returns:
            List[Dict]: List of events
        """
        if event_type:
            return [event for event in self.events if event["type"] == event_type]
        return self.events.copy()
    
    def _emit_transfer(self, from_addr: str, to_addr: str, amount: int) -> None:
        """Emit a Transfer event."""
        self.events.append({
            "type": "Transfer",
            "from": from_addr,
            "to": to_addr,
            "value": amount,
            "block_number": len(self.events) + 1  # Simulated block number
        })
    
    def _emit_approval(self, owner: str, spender: str, amount: int) -> None:
        """Emit an Approval event."""
        self.events.append({
            "type": "Approval",
            "owner": owner,
            "spender": spender,
            "value": amount,
            "block_number": len(self.events) + 1  # Simulated block number
        })
    
    # Utility functions for human-readable amounts
    def to_tokens(self, wei_amount: int) -> float:
        """Convert wei amount to human-readable tokens."""
        return wei_amount / (10 ** self.decimals)
    
    def to_wei(self, token_amount: float) -> int:
        """Convert human-readable tokens to wei."""
        return int(token_amount * (10 ** self.decimals))
