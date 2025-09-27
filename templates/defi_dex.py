"""
Decentralized Exchange (DEX) Template

A simple AMM-style DEX for token swapping on 0G Galileo.
Features automated market making with constant product formula.
"""

from typing import Dict, Tuple, Optional
import math


class SimpleDEX:
    """
    Automated Market Maker DEX for 0G Galileo.
    
    Features:
    - Token pair liquidity pools
    - Constant product AMM (x * y = k)
    - Liquidity provider rewards
    - Slippage protection
    """
    
    def __init__(self, owner: str, fee_rate: int = 30):  # 0.3% fee
        """Initialize DEX."""
        self.owner = owner
        self.fee_rate = fee_rate  # Fee in basis points (30 = 0.3%)
        
        # Liquidity pools: pair_id -> {token_a_reserve, token_b_reserve, total_liquidity}
        self.pools: Dict[str, Dict] = {}
        
        # Liquidity provider shares: pair_id -> {provider -> shares}
        self.lp_shares: Dict[str, Dict[str, int]] = {}
        
        # Trading pairs: token_a + token_b -> pair_id
        self.trading_pairs: Dict[str, str] = {}
        
        # Fee collection
        self.collected_fees: Dict[str, Dict[str, int]] = {}
    
    def create_pair(
        self, 
        caller: str, 
        token_a: str, 
        token_b: str
    ) -> bool:
        """Create a new trading pair."""
        if caller != self.owner:
            return False
        
        # Ensure consistent pair ordering
        if token_a > token_b:
            token_a, token_b = token_b, token_a
        
        pair_key = f"{token_a}_{token_b}"
        pair_id = f"pair_{len(self.pools)}"
        
        if pair_key in self.trading_pairs:
            return False  # Pair already exists
        
        # Initialize pool
        self.pools[pair_id] = {
            "token_a": token_a,
            "token_b": token_b,
            "reserve_a": 0,
            "reserve_b": 0,
            "total_liquidity": 0,
            "k_constant": 0
        }
        
        self.lp_shares[pair_id] = {}
        self.collected_fees[pair_id] = {"token_a": 0, "token_b": 0}
        self.trading_pairs[pair_key] = pair_id
        
        return True
    
    def add_liquidity(
        self, 
        caller: str, 
        token_a: str, 
        token_b: str, 
        amount_a: int, 
        amount_b: int
    ) -> Tuple[bool, int]:
        """Add liquidity to a pool."""
        # Get pair
        if token_a > token_b:
            token_a, token_b = token_b, token_a
            amount_a, amount_b = amount_b, amount_a
        
        pair_key = f"{token_a}_{token_b}"
        if pair_key not in self.trading_pairs:
            return False, 0
        
        pair_id = self.trading_pairs[pair_key]
        pool = self.pools[pair_id]
        
        # Calculate liquidity shares
        if pool["total_liquidity"] == 0:
            # First liquidity provision
            liquidity_shares = int(math.sqrt(amount_a * amount_b))
        else:
            # Proportional liquidity provision
            share_a = (amount_a * pool["total_liquidity"]) // pool["reserve_a"]
            share_b = (amount_b * pool["total_liquidity"]) // pool["reserve_b"]
            liquidity_shares = min(share_a, share_b)
        
        # Update pool reserves
        pool["reserve_a"] += amount_a
        pool["reserve_b"] += amount_b
        pool["total_liquidity"] += liquidity_shares
        pool["k_constant"] = pool["reserve_a"] * pool["reserve_b"]
        
        # Update LP shares
        if caller not in self.lp_shares[pair_id]:
            self.lp_shares[pair_id][caller] = 0
        self.lp_shares[pair_id][caller] += liquidity_shares
        
        return True, liquidity_shares
    
    def remove_liquidity(
        self, 
        caller: str, 
        token_a: str, 
        token_b: str, 
        liquidity_shares: int
    ) -> Tuple[bool, int, int]:
        """Remove liquidity from a pool."""
        # Get pair
        if token_a > token_b:
            token_a, token_b = token_b, token_a
        
        pair_key = f"{token_a}_{token_b}"
        if pair_key not in self.trading_pairs:
            return False, 0, 0
        
        pair_id = self.trading_pairs[pair_key]
        pool = self.pools[pair_id]
        
        # Check LP shares
        if (caller not in self.lp_shares[pair_id] or 
            self.lp_shares[pair_id][caller] < liquidity_shares):
            return False, 0, 0
        
        # Calculate withdrawal amounts
        total_liquidity = pool["total_liquidity"]
        amount_a = (liquidity_shares * pool["reserve_a"]) // total_liquidity
        amount_b = (liquidity_shares * pool["reserve_b"]) // total_liquidity
        
        # Update pool
        pool["reserve_a"] -= amount_a
        pool["reserve_b"] -= amount_b
        pool["total_liquidity"] -= liquidity_shares
        pool["k_constant"] = pool["reserve_a"] * pool["reserve_b"]
        
        # Update LP shares
        self.lp_shares[pair_id][caller] -= liquidity_shares
        
        return True, amount_a, amount_b
    
    def swap_tokens(
        self, 
        caller: str, 
        token_in: str, 
        token_out: str, 
        amount_in: int,
        min_amount_out: int = 0
    ) -> Tuple[bool, int]:
        """Swap tokens using AMM."""
        # Get pair
        token_a, token_b = (token_in, token_out) if token_in < token_out else (token_out, token_in)
        pair_key = f"{token_a}_{token_b}"
        
        if pair_key not in self.trading_pairs:
            return False, 0
        
        pair_id = self.trading_pairs[pair_key]
        pool = self.pools[pair_id]
        
        # Determine input/output reserves
        if token_in == token_a:
            reserve_in = pool["reserve_a"]
            reserve_out = pool["reserve_b"]
        else:
            reserve_in = pool["reserve_b"]
            reserve_out = pool["reserve_a"]
        
        # Calculate output amount using constant product formula
        # (x + dx) * (y - dy) = k
        # dy = (y * dx) / (x + dx)
        
        # Apply fee
        amount_in_with_fee = amount_in * (10000 - self.fee_rate) // 10000
        
        # Calculate output
        numerator = amount_in_with_fee * reserve_out
        denominator = reserve_in + amount_in_with_fee
        amount_out = numerator // denominator
        
        # Check slippage protection
        if amount_out < min_amount_out:
            return False, 0
        
        # Update reserves
        if token_in == token_a:
            pool["reserve_a"] += amount_in
            pool["reserve_b"] -= amount_out
        else:
            pool["reserve_b"] += amount_in
            pool["reserve_a"] -= amount_out
        
        # Collect fees
        fee_amount = amount_in - amount_in_with_fee
        fee_token = "token_a" if token_in == token_a else "token_b"
        self.collected_fees[pair_id][fee_token] += fee_amount
        
        return True, amount_out
    
    def get_price(self, token_a: str, token_b: str) -> Optional[float]:
        """Get current price of token_a in terms of token_b."""
        if token_a > token_b:
            token_a, token_b = token_b, token_a
            inverse = True
        else:
            inverse = False
        
        pair_key = f"{token_a}_{token_b}"
        if pair_key not in self.trading_pairs:
            return None
        
        pair_id = self.trading_pairs[pair_key]
        pool = self.pools[pair_id]
        
        if pool["reserve_a"] == 0 or pool["reserve_b"] == 0:
            return None
        
        price = pool["reserve_b"] / pool["reserve_a"]
        return 1 / price if inverse else price
    
    def get_pool_info(self, token_a: str, token_b: str) -> Optional[Dict]:
        """Get pool information."""
        if token_a > token_b:
            token_a, token_b = token_b, token_a
        
        pair_key = f"{token_a}_{token_b}"
        if pair_key not in self.trading_pairs:
            return None
        
        pair_id = self.trading_pairs[pair_key]
        pool = self.pools[pair_id].copy()
        
        # Add calculated fields
        if pool["reserve_a"] > 0 and pool["reserve_b"] > 0:
            pool["price_a_to_b"] = pool["reserve_b"] / pool["reserve_a"]
            pool["price_b_to_a"] = pool["reserve_a"] / pool["reserve_b"]
        else:
            pool["price_a_to_b"] = 0
            pool["price_b_to_a"] = 0
        
        return pool
    
    def get_lp_balance(self, caller: str, token_a: str, token_b: str) -> int:
        """Get liquidity provider balance."""
        if token_a > token_b:
            token_a, token_b = token_b, token_a
        
        pair_key = f"{token_a}_{token_b}"
        if pair_key not in self.trading_pairs:
            return 0
        
        pair_id = self.trading_pairs[pair_key]
        return self.lp_shares[pair_id].get(caller, 0)
