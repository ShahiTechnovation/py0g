"""
Advanced Staking Contract for 0G Galileo

A comprehensive staking contract that allows users to stake tokens,
earn rewards, and participate in governance. Features include:
- Token staking with flexible lock periods
- Reward distribution based on staking duration
- Early withdrawal penalties
- Governance voting power based on stake
- Multi-tier reward rates
"""

from typing import Dict, Tuple, Optional
import time


class StakingContract:
    """
    Advanced Staking Contract for 0G Galileo Blockchain.
    
    Features:
    - Flexible staking periods (30, 90, 180, 365 days)
    - Tiered reward rates based on lock duration
    - Early withdrawal with penalties
    - Governance voting power
    - Compound staking rewards
    - Emergency pause functionality
    """
    
    def __init__(self, owner: str, reward_token: str, staking_token: str):
        """
        Initialize the staking contract.
        
        Args:
            owner: Contract owner address
            reward_token: Address of reward token contract
            staking_token: Address of staking token contract
        """
        self.owner = owner
        self.reward_token = reward_token
        self.staking_token = staking_token
        
        # Contract state
        self.paused = False
        self.total_staked = 0
        self.total_rewards_distributed = 0
        
        # Staking pools by duration (days)
        self.staking_pools = {
            30: {"apy": 500, "total_staked": 0},    # 5% APY
            90: {"apy": 800, "total_staked": 0},    # 8% APY
            180: {"apy": 1200, "total_staked": 0},  # 12% APY
            365: {"apy": 1800, "total_staked": 0}   # 18% APY
        }
        
        # User stakes: user -> [stake_id -> stake_info]
        self.user_stakes: Dict[str, Dict[int, Dict]] = {}
        
        # Global stake counter
        self.next_stake_id = 1
        
        # Governance: user -> voting_power
        self.voting_power: Dict[str, int] = {}
        
        # Emergency settings
        self.emergency_withdrawal_penalty = 2000  # 20%
        
    def stake_tokens(
        self, 
        staker: str, 
        amount: int, 
        lock_days: int
    ) -> Tuple[bool, int]:
        """
        Stake tokens for a specific duration.
        
        Args:
            staker: Address of the staker
            amount: Amount of tokens to stake
            lock_days: Lock period in days (30, 90, 180, 365)
            
        Returns:
            Tuple[bool, int]: (success, stake_id)
        """
        if self.paused:
            return False, 0
            
        if lock_days not in self.staking_pools:
            return False, 0
            
        if amount <= 0:
            return False, 0
        
        # Create stake record
        stake_id = self.next_stake_id
        self.next_stake_id += 1
        
        current_time = int(time.time())  # Simplified timestamp
        unlock_time = current_time + (lock_days * 24 * 3600)
        
        stake_info = {
            "amount": amount,
            "lock_days": lock_days,
            "start_time": current_time,
            "unlock_time": unlock_time,
            "last_reward_time": current_time,
            "accumulated_rewards": 0,
            "active": True
        }
        
        # Initialize user stakes if needed
        if staker not in self.user_stakes:
            self.user_stakes[staker] = {}
            self.voting_power[staker] = 0
        
        # Record stake
        self.user_stakes[staker][stake_id] = stake_info
        
        # Update totals
        self.total_staked += amount
        self.staking_pools[lock_days]["total_staked"] += amount
        
        # Update voting power (longer locks = more power)
        voting_multiplier = lock_days // 30  # 1x for 30 days, 12x for 365 days
        self.voting_power[staker] += amount * voting_multiplier
        
        return True, stake_id
    
    def unstake_tokens(self, staker: str, stake_id: int) -> Tuple[bool, int, int]:
        """
        Unstake tokens after lock period.
        
        Args:
            staker: Address of the staker
            stake_id: ID of the stake to unstake
            
        Returns:
            Tuple[bool, int, int]: (success, principal_amount, reward_amount)
        """
        if self.paused:
            return False, 0, 0
            
        if (staker not in self.user_stakes or 
            stake_id not in self.user_stakes[staker]):
            return False, 0, 0
        
        stake = self.user_stakes[staker][stake_id]
        if not stake["active"]:
            return False, 0, 0
        
        current_time = int(time.time())
        
        # Check if lock period is over
        if current_time < stake["unlock_time"]:
            return False, 0, 0
        
        # Calculate final rewards
        rewards = self._calculate_rewards(staker, stake_id)
        principal = stake["amount"]
        
        # Update state
        stake["active"] = False
        stake["accumulated_rewards"] += rewards
        
        # Update totals
        self.total_staked -= principal
        self.staking_pools[stake["lock_days"]]["total_staked"] -= principal
        self.total_rewards_distributed += rewards
        
        # Update voting power
        voting_multiplier = stake["lock_days"] // 30
        self.voting_power[staker] -= principal * voting_multiplier
        
        return True, principal, rewards
    
    def emergency_withdraw(self, staker: str, stake_id: int) -> Tuple[bool, int, int]:
        """
        Emergency withdrawal with penalty.
        
        Args:
            staker: Address of the staker
            stake_id: ID of the stake to withdraw
            
        Returns:
            Tuple[bool, int, int]: (success, amount_returned, penalty_amount)
        """
        if (staker not in self.user_stakes or 
            stake_id not in self.user_stakes[staker]):
            return False, 0, 0
        
        stake = self.user_stakes[staker][stake_id]
        if not stake["active"]:
            return False, 0, 0
        
        principal = stake["amount"]
        penalty = (principal * self.emergency_withdrawal_penalty) // 10000
        amount_returned = principal - penalty
        
        # Update state
        stake["active"] = False
        
        # Update totals
        self.total_staked -= principal
        self.staking_pools[stake["lock_days"]]["total_staked"] -= principal
        
        # Update voting power
        voting_multiplier = stake["lock_days"] // 30
        self.voting_power[staker] -= principal * voting_multiplier
        
        return True, amount_returned, penalty
    
    def claim_rewards(self, staker: str, stake_id: int) -> Tuple[bool, int]:
        """
        Claim accumulated rewards without unstaking.
        
        Args:
            staker: Address of the staker
            stake_id: ID of the stake
            
        Returns:
            Tuple[bool, int]: (success, reward_amount)
        """
        if (staker not in self.user_stakes or 
            stake_id not in self.user_stakes[staker]):
            return False, 0
        
        stake = self.user_stakes[staker][stake_id]
        if not stake["active"]:
            return False, 0
        
        rewards = self._calculate_rewards(staker, stake_id)
        
        if rewards > 0:
            stake["last_reward_time"] = int(time.time())
            stake["accumulated_rewards"] += rewards
            self.total_rewards_distributed += rewards
        
        return True, rewards
    
    def compound_rewards(self, staker: str, stake_id: int) -> Tuple[bool, int]:
        """
        Compound rewards back into the stake.
        
        Args:
            staker: Address of the staker
            stake_id: ID of the stake
            
        Returns:
            Tuple[bool, int]: (success, compounded_amount)
        """
        if (staker not in self.user_stakes or 
            stake_id not in self.user_stakes[staker]):
            return False, 0
        
        stake = self.user_stakes[staker][stake_id]
        if not stake["active"]:
            return False, 0
        
        rewards = self._calculate_rewards(staker, stake_id)
        
        if rewards > 0:
            # Add rewards to principal
            stake["amount"] += rewards
            stake["last_reward_time"] = int(time.time())
            
            # Update totals
            self.total_staked += rewards
            self.staking_pools[stake["lock_days"]]["total_staked"] += rewards
            
            # Update voting power
            voting_multiplier = stake["lock_days"] // 30
            self.voting_power[staker] += rewards * voting_multiplier
        
        return True, rewards
    
    def _calculate_rewards(self, staker: str, stake_id: int) -> int:
        """Calculate pending rewards for a stake."""
        stake = self.user_stakes[staker][stake_id]
        
        current_time = int(time.time())
        time_staked = current_time - stake["last_reward_time"]
        
        if time_staked <= 0:
            return 0
        
        # Calculate rewards based on APY
        apy = self.staking_pools[stake["lock_days"]]["apy"]
        annual_reward = (stake["amount"] * apy) // 10000
        
        # Convert to time-based reward (simplified)
        seconds_per_year = 365 * 24 * 3600
        rewards = (annual_reward * time_staked) // seconds_per_year
        
        return rewards
    
    def get_stake_info(self, staker: str, stake_id: int) -> Optional[Dict]:
        """Get detailed information about a stake."""
        if (staker not in self.user_stakes or 
            stake_id not in self.user_stakes[staker]):
            return None
        
        stake = self.user_stakes[staker][stake_id].copy()
        
        # Add calculated fields
        current_time = int(time.time())
        stake["time_remaining"] = max(0, stake["unlock_time"] - current_time)
        stake["pending_rewards"] = self._calculate_rewards(staker, stake_id)
        stake["is_unlocked"] = current_time >= stake["unlock_time"]
        
        return stake
    
    def get_user_total_stake(self, staker: str) -> int:
        """Get total staked amount for a user."""
        if staker not in self.user_stakes:
            return 0
        
        total = 0
        for stake in self.user_stakes[staker].values():
            if stake["active"]:
                total += stake["amount"]
        
        return total
    
    def get_user_voting_power(self, staker: str) -> int:
        """Get voting power for a user."""
        return self.voting_power.get(staker, 0)
    
    def get_pool_stats(self, lock_days: int) -> Optional[Dict]:
        """Get statistics for a staking pool."""
        if lock_days not in self.staking_pools:
            return None
        
        pool = self.staking_pools[lock_days].copy()
        pool["lock_days"] = lock_days
        
        return pool
    
    def get_contract_stats(self) -> Dict:
        """Get overall contract statistics."""
        return {
            "total_staked": self.total_staked,
            "total_rewards_distributed": self.total_rewards_distributed,
            "total_stakers": len(self.user_stakes),
            "paused": self.paused,
            "pools": self.staking_pools
        }
    
    def pause_contract(self, caller: str) -> bool:
        """Pause the contract (owner only)."""
        if caller != self.owner:
            return False
        
        self.paused = True
        return True
    
    def unpause_contract(self, caller: str) -> bool:
        """Unpause the contract (owner only)."""
        if caller != self.owner:
            return False
        
        self.paused = False
        return True
    
    def set_emergency_penalty(self, caller: str, penalty_bps: int) -> bool:
        """Set emergency withdrawal penalty (owner only)."""
        if caller != self.owner:
            return False
        
        if penalty_bps > 5000:  # Max 50% penalty
            return False
        
        self.emergency_withdrawal_penalty = penalty_bps
        return True
    
    def get_owner(self) -> str:
        """Get contract owner."""
        return self.owner
