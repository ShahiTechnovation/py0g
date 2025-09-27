"""
Project Initializer for py0g Smart Contract Projects

Creates new Python smart contract projects with proper structure,
example contracts, and configuration files.
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass
import shutil


@dataclass
class ProjectTemplate:
    """Template for a new py0g project."""
    project_name: str
    contract_name: str
    description: str
    template_type: str
    files: Dict[str, str]  # filename -> content


class ProjectInitializer:
    """
    Initializes new py0g smart contract projects.
    
    Creates project structure with:
    - Example contracts
    - Configuration files  
    - Directory structure
    - Development files
    """
    
    def __init__(self):
        """Initialize the project generator."""
        self.templates = {
            "token": self._create_token_template(),
            "basic": self._create_basic_template(),
            "nft": self._create_nft_template(),
            "defi": self._create_defi_template()
        }
    
    def init_project(self, project_name: str, template_type: str = "basic", 
                     directory: Optional[str] = None) -> str:
        """
        Initialize a new py0g project.
        
        Args:
            project_name: Name of the project
            template_type: Type of template (basic, token, nft, defi)
            directory: Target directory (defaults to project_name)
            
        Returns:
            str: Path to created project directory
        """
        # Determine project directory
        if directory is None:
            directory = project_name
        
        project_path = Path(directory).resolve()
        
        # Check if directory already exists
        if project_path.exists():
            raise ValueError(f"Directory '{project_path}' already exists")
        
        # Get template
        if template_type not in self.templates:
            raise ValueError(f"Unknown template type '{template_type}'. Available: {list(self.templates.keys())}")
        
        template = self.templates[template_type]
        
        # Create project structure
        self._create_project_structure(project_path)
        
        self._generate_project_files(project_path, template, project_name)
        
        # Create configuration files
        self._create_config_files(project_path, project_name)
        
        return str(project_path)
    
    def list_templates(self) -> Dict[str, str]:
        """
        List available project templates.
        
        Returns:
            Dict[str, str]: Template names and descriptions
        """
        return {
            "basic": "Basic smart contract with data storage and counter functionality",
            "token": "ERC-20 style fungible token with transfer and allowance features",
            "nft": "ERC-721 style non-fungible token with minting and metadata",
            "defi": "DeFi staking contract with reward distribution"
        }
    
    def _create_project_structure(self, project_path: Path):
        """Create the basic project directory structure."""
        # Create main directories
        directories = [
            "contracts",
            "artifacts", 
            "tests",
            "scripts",
            "docs"
        ]
        
        for directory in directories:
            (project_path / directory).mkdir(parents=True, exist_ok=True)
    
    def _generate_project_files(self, project_path: Path, template: ProjectTemplate, project_name: str):
        """Generate project files from template."""
        for filename, content in template.files.items():
            # Replace template variables in filename
            actual_filename = filename.replace("{{CONTRACT_NAME}}", project_name)
            actual_filename = actual_filename.replace("{{PROJECT_NAME}}", project_name)
            
            file_path = project_path / actual_filename
            
            # Replace template variables in content
            content = content.replace("{{PROJECT_NAME}}", project_name)
            content = content.replace("{{CONTRACT_NAME}}", project_name)
            content = content.replace("{{DESCRIPTION}}", f"A smart contract for {project_name}")
            
            # Ensure parent directory exists
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Write file
            file_path.write_text(content)
    
    def _create_config_files(self, project_path: Path, project_name: str):
        """Create configuration files for the project."""
        # Create .gitignore
        gitignore_content = """# py0g artifacts
artifacts/
*.bin
*.abi.json
*_hash.json
*_proof.json
*_deployment.json

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Environment variables
.env
.env.local
.env.*.local

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Logs
*.log

# Private keys (IMPORTANT: Never commit private keys)
*.key
*.pem
"""
        (project_path / ".gitignore").write_text(gitignore_content)
        
        # Create py0g.config.json
        config = {
            "project_name": project_name,
            "version": "1.0.0",
            "py0g_version": "0.2.0",
            "default_network": "0g_galileo_testnet",
            "networks": {
                "0g_galileo_testnet": {
                    "rpc_url": "https://evmrpc-testnet.0g.ai",
                    "chain_id": 16602,
                    "explorer_url": "https://chainscan-galileo.0g.ai"
                }
            },
            "compiler": {
                "optimization": True,
                "target": "0g_evm"
            },
            "artifacts_dir": "artifacts",
            "contracts_dir": "contracts"
        }
        
        config_file = project_path / "py0g.config.json"
        config_file.write_text(json.dumps(config, indent=2))
        
        # Create README.md
        readme_content = f"""# {project_name}

A Python-first smart contract project built with py0g for the 0G Galileo blockchain.

## Getting Started

### Prerequisites

- Python 3.11+
- py0g CLI toolkit

### Installation

1. Install py0g if you haven't already:
```bash
pip install py0g
```

2. Navigate to your project directory:
```bash
cd {project_name}
```

### Development Workflow

1. **Compile your contracts:**
```bash
py0g compile contracts/YourContract.py
```

2. **Generate program hash:**
```bash
py0g hash contracts/YourContract.py
```

3. **Generate zero-knowledge proof:**
```bash
py0g prove contracts/YourContract.py
```

4. **Test deployment (simulation):**
```bash
py0g deploy contracts/YourContract.py --simulate
```

5. **Deploy to 0G Galileo testnet:**
```bash
# Set your private key as environment variable
export ZERO_G_PRIVATE_KEY=your_private_key_here

# Deploy to testnet
py0g deploy contracts/YourContract.py
```

6. **Verify contract:**
```bash
py0g verify contracts/YourContract.py
```

### Project Structure

```
{project_name}/
|-- contracts/          # Python smart contracts
|-- artifacts/          # Compiled bytecode and metadata
|-- tests/             # Contract tests
|-- scripts/           # Deployment and utility scripts
|-- docs/              # Documentation
|-- py0g.config.json   # Project configuration
|-- README.md          # This file
```

### Configuration

Edit `py0g.config.json` to configure:
- Network settings
- Compiler options
- Artifact paths

### Security

- Never commit private keys to version control
- Use environment variables for sensitive data
- Test on testnet before mainnet deployment

## Learn More

- [py0g Documentation](https://github.com/py0g/py0g)
- [0G Galileo Blockchain](https://0g.ai)
- [Python Smart Contract Patterns](https://github.com/py0g/examples)
"""
        
        (project_path / "README.md").write_text(readme_content)
    
    def _create_basic_template(self) -> ProjectTemplate:
        """Create basic contract template."""
        contract_content = '''"""
{{CONTRACT_NAME}} - A basic Python smart contract

{{DESCRIPTION}}
"""

from typing import Dict, Any


class {{CONTRACT_NAME}}:
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
'''
        
        test_content = '''"""
Tests for {{CONTRACT_NAME}}

Run with: python -m pytest tests/
"""

import pytest
from contracts.{{CONTRACT_NAME}} import {{CONTRACT_NAME}}


class Test{{CONTRACT_NAME}}:
    """Test suite for {{CONTRACT_NAME}} contract."""
    
    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.owner = "0x1234567890123456789012345678901234567890"
        self.contract = {{CONTRACT_NAME}}(self.owner)
    
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
'''
        
        deploy_script = '''"""
Deployment script for {{CONTRACT_NAME}}

Usage: python scripts/deploy.py
"""

import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from py0g.compiler import PythonContractCompiler
from py0g.hasher import ProgramHasher
from py0g.prover import ZKProver
from py0g.deployer import ContractDeployer


def main():
    """Deploy {{CONTRACT_NAME}} to 0G Galileo."""
    contract_path = "contracts/{{CONTRACT_NAME}}.py"
    
    print(f"Deploying {contract_path}")
    
    # Check if contract exists
    if not Path(contract_path).exists():
        print(f"Contract file not found: {contract_path}")
        sys.exit(1)
    
    try:
        # 1. Compile contract
        print("Compiling contract...")
        compiler = PythonContractCompiler()
        result = compiler.compile_contract(contract_path)
        compiler.save_artifacts(result, "{{CONTRACT_NAME}}", "artifacts")
        print("Compilation complete")
        
        # 2. Generate hash
        print("Generating program hash...")
        hasher = ProgramHasher()
        program_hash = hasher.hash_contract(contract_path)
        hasher.save_hash(program_hash, "artifacts")
        print("Hash generation complete")
        
        # 3. Generate proof
        print("Generating ZK proof...")
        prover = ZKProver()
        proof = prover.generate_proof(contract_path, program_hash.program_hash)
        prover.save_proof(proof, "artifacts")
        print("Proof generation complete")
        
        # 4. Deploy (simulation mode by default)
        print("Simulating deployment...")
        deployer = ContractDeployer()
        simulation = deployer.simulate_deployment(
            result.bytecode, 
            program_hash.program_hash, 
            ""
        )
        
        print("Simulation successful!")
        print(f"  Estimated Address: {simulation['contract_address']}")
        print(f"  Estimated Gas: {simulation['estimated_gas']}")
        print(f"  Estimated Cost: {simulation['estimated_cost']}")
        
    except Exception as e:
        print(f"Deployment failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
'''
        
        return ProjectTemplate(
            project_name="{{PROJECT_NAME}}",
            contract_name="{{CONTRACT_NAME}}",
            description="{{DESCRIPTION}}",
            template_type="basic",
            files={
                "contracts/{{CONTRACT_NAME}}.py": contract_content,
                "tests/test_{{CONTRACT_NAME}}.py": test_content,
                "scripts/deploy.py": deploy_script
            }
        )
    
    def _create_token_template(self) -> ProjectTemplate:
        """Create ERC-20 style token template."""
        token_content = '''"""
{{CONTRACT_NAME}} - ERC-20 style token contract

{{DESCRIPTION}}
"""

from typing import Dict


class {{CONTRACT_NAME}}:
    """
    ERC-20 style token implementation in Python.
    
    This contract implements a fungible token with transfer,
    approve, and allowance functionality.
    """
    
    def __init__(self, name: str, symbol: str, total_supply: int, owner: str):
        """
        Initialize the token contract.
        
        Args:
            name: Token name (e.g., "My Token")
            symbol: Token symbol (e.g., "MTK")
            total_supply: Total token supply
            owner: Contract owner address
        """
        self.name: str = name
        self.symbol: str = symbol
        self.decimals: int = 18
        self.total_supply: int = total_supply
        self.owner: str = owner
        
        # Token balances
        self.balances: Dict[str, int] = {owner: total_supply}
        
        # Allowances (owner -> spender -> amount)
        self.allowances: Dict[str, Dict[str, int]] = {}
    
    def balance_of(self, account: str) -> int:
        """
        Get token balance for an account.
        
        Args:
            account: Account address
            
        Returns:
            int: Token balance
        """
        return self.balances.get(account, 0)
    
    def transfer(self, sender: str, to: str, amount: int) -> bool:
        """
        Transfer tokens from sender to recipient.
        
        Args:
            sender: Sender address
            to: Recipient address
            amount: Amount to transfer
            
        Returns:
            bool: True if successful
        """
        if self.balance_of(sender) < amount:
            return False
        
        if amount <= 0:
            return False
        
        # Perform transfer
        self.balances[sender] = self.balances.get(sender, 0) - amount
        self.balances[to] = self.balances.get(to, 0) + amount
        
        return True
    
    def approve(self, owner: str, spender: str, amount: int) -> bool:
        """
        Approve spender to spend tokens on behalf of owner.
        
        Args:
            owner: Token owner address
            spender: Spender address
            amount: Amount to approve
            
        Returns:
            bool: True if successful
        """
        if owner not in self.allowances:
            self.allowances[owner] = {}
        
        self.allowances[owner][spender] = amount
        return True
    
    def allowance(self, owner: str, spender: str) -> int:
        """
        Get the allowance for a spender.
        
        Args:
            owner: Token owner address
            spender: Spender address
            
        Returns:
            int: Approved amount
        """
        return self.allowances.get(owner, {}).get(spender, 0)
    
    def transfer_from(self, spender: str, from_addr: str, to: str, amount: int) -> bool:
        """
        Transfer tokens from one address to another using allowance.
        
        Args:
            spender: Address spending the tokens
            from_addr: Address to transfer from
            to: Address to transfer to
            amount: Amount to transfer
            
        Returns:
            bool: True if successful
        """
        current_allowance = self.allowance(from_addr, spender)
        
        if current_allowance < amount:
            return False
        
        if self.balance_of(from_addr) < amount:
            return False
        
        # Perform transfer
        if self.transfer(from_addr, to, amount):
            # Update allowance
            self.allowances[from_addr][spender] = current_allowance - amount
            return True
        
        return False
    
    def mint(self, caller: str, to: str, amount: int) -> bool:
        """
        Mint new tokens (only owner).
        
        Args:
            caller: Address calling this function
            to: Address to mint tokens to
            amount: Amount to mint
            
        Returns:
            bool: True if successful
        """
        if caller != self.owner:
            return False
        
        self.total_supply += amount
        self.balances[to] = self.balances.get(to, 0) + amount
        return True
    
    def burn(self, caller: str, amount: int) -> bool:
        """
        Burn tokens from caller's balance.
        
        Args:
            caller: Address calling this function
            amount: Amount to burn
            
        Returns:
            bool: True if successful
        """
        if self.balance_of(caller) < amount:
            return False
        
        self.balances[caller] -= amount
        self.total_supply -= amount
        return True
'''
        
        return ProjectTemplate(
            project_name="{{PROJECT_NAME}}",
            contract_name="{{CONTRACT_NAME}}",
            description="{{DESCRIPTION}}",
            template_type="token",
            files={
                "contracts/{{CONTRACT_NAME}}.py": token_content
            }
        )
    
    def _create_nft_template(self) -> ProjectTemplate:
        """Create NFT contract template."""
        nft_content = '''"""
{{CONTRACT_NAME}} - NFT contract

{{DESCRIPTION}}
"""

from typing import Dict, Optional


class {{CONTRACT_NAME}}:
    """
    ERC-721 style NFT implementation in Python.
    
    This contract implements non-fungible tokens with
    minting, ownership tracking, and transfer functionality.
    """
    
    def __init__(self, name: str, symbol: str, owner: str):
        """
        Initialize the NFT contract.
        
        Args:
            name: NFT collection name
            symbol: NFT collection symbol
            owner: Contract owner address
        """
        self.name: str = name
        self.symbol: str = symbol
        self.owner: str = owner
        
        # Token ownership mapping
        self.owners: Dict[int, str] = {}
        
        # Owner balance mapping
        self.balances: Dict[str, int] = {}
        
        # Token approvals
        self.token_approvals: Dict[int, str] = {}
        
        # Operator approvals
        self.operator_approvals: Dict[str, Dict[str, bool]] = {}
        
        # Token metadata
        self.token_uris: Dict[int, str] = {}
        
        # Current token ID
        self.current_token_id: int = 0
    
    def balance_of(self, owner: str) -> int:
        """
        Get number of NFTs owned by an address.
        
        Args:
            owner: Owner address
            
        Returns:
            int: Number of NFTs owned
        """
        return self.balances.get(owner, 0)
    
    def owner_of(self, token_id: int) -> Optional[str]:
        """
        Get owner of a specific token.
        
        Args:
            token_id: Token ID
            
        Returns:
            Optional[str]: Owner address or None if token doesn't exist
        """
        return self.owners.get(token_id)
    
    def token_uri(self, token_id: int) -> Optional[str]:
        """
        Get metadata URI for a token.
        
        Args:
            token_id: Token ID
            
        Returns:
            Optional[str]: Token URI or None if not set
        """
        return self.token_uris.get(token_id)
    
    def mint(self, caller: str, to: str, token_uri: str = "") -> int:
        """
        Mint a new NFT (only owner).
        
        Args:
            caller: Address calling this function
            to: Address to mint to
            token_uri: Metadata URI for the token
            
        Returns:
            int: Token ID of minted NFT
        """
        if caller != self.owner:
            raise ValueError("Only owner can mint")
        
        token_id = self.current_token_id
        self.current_token_id += 1
        
        # Set ownership
        self.owners[token_id] = to
        self.balances[to] = self.balances.get(to, 0) + 1
        
        # Set metadata
        if token_uri:
            self.token_uris[token_id] = token_uri
        
        return token_id
    
    def transfer_from(self, caller: str, from_addr: str, to: str, token_id: int) -> bool:
        """
        Transfer NFT from one address to another.
        
        Args:
            caller: Address calling this function
            from_addr: Current owner address
            to: New owner address
            token_id: Token ID to transfer
            
        Returns:
            bool: True if successful
        """
        # Check if token exists
        if token_id not in self.owners:
            return False
        
        # Check ownership
        if self.owners[token_id] != from_addr:
            return False
        
        # Check permissions
        if not self._is_approved_or_owner(caller, token_id):
            return False
        
        # Clear approvals
        if token_id in self.token_approvals:
            del self.token_approvals[token_id]
        
        # Update ownership
        self.owners[token_id] = to
        self.balances[from_addr] -= 1
        self.balances[to] = self.balances.get(to, 0) + 1
        
        return True
    
    def approve(self, caller: str, to: str, token_id: int) -> bool:
        """
        Approve another address to transfer a specific token.
        
        Args:
            caller: Token owner address
            to: Address to approve
            token_id: Token ID
            
        Returns:
            bool: True if successful
        """
        if self.owners.get(token_id) != caller:
            return False
        
        self.token_approvals[token_id] = to
        return True
    
    def set_approval_for_all(self, caller: str, operator: str, approved: bool) -> bool:
        """
        Approve or remove approval for all tokens.
        
        Args:
            caller: Token owner address
            operator: Operator address
            approved: Whether to approve or revoke
            
        Returns:
            bool: True if successful
        """
        if caller not in self.operator_approvals:
            self.operator_approvals[caller] = {}
        
        self.operator_approvals[caller][operator] = approved
        return True
    
    def get_approved(self, token_id: int) -> Optional[str]:
        """
        Get approved address for a token.
        
        Args:
            token_id: Token ID
            
        Returns:
            Optional[str]: Approved address or None
        """
        return self.token_approvals.get(token_id)
    
    def is_approved_for_all(self, owner: str, operator: str) -> bool:
        """
        Check if operator is approved for all owner's tokens.
        
        Args:
            owner: Owner address
            operator: Operator address
            
        Returns:
            bool: True if approved for all
        """
        return self.operator_approvals.get(owner, {}).get(operator, False)
    
    def _is_approved_or_owner(self, spender: str, token_id: int) -> bool:
        """Check if address is approved or owner of token."""
        owner = self.owner_of(token_id)
        if not owner:
            return False
        
        return (spender == owner or 
                self.get_approved(token_id) == spender or
                self.is_approved_for_all(owner, spender))
'''
        
        return ProjectTemplate(
            project_name="{{PROJECT_NAME}}",
            contract_name="{{CONTRACT_NAME}}",
            description="{{DESCRIPTION}}",
            template_type="nft",
            files={
                "contracts/{{CONTRACT_NAME}}.py": nft_content
            }
        )
    
    def _create_defi_template(self) -> ProjectTemplate:
        """Create DeFi contract template."""
        defi_content = '''"""
{{CONTRACT_NAME}} - DeFi staking contract

{{DESCRIPTION}}
"""

from typing import Dict
import time


class {{CONTRACT_NAME}}:
    """
    Simple staking contract for DeFi applications.
    
    Users can stake tokens and earn rewards over time.
    """
    
    def __init__(self, reward_token: str, staking_token: str, owner: str):
        """
        Initialize the staking contract.
        
        Args:
            reward_token: Address of reward token contract
            staking_token: Address of staking token contract
            owner: Contract owner address
        """
        self.reward_token: str = reward_token
        self.staking_token: str = staking_token
        self.owner: str = owner
        
        # Staking data
        self.stakes: Dict[str, int] = {}  # user -> staked amount
        self.stake_timestamps: Dict[str, int] = {}  # user -> stake timestamp
        self.rewards_claimed: Dict[str, int] = {}  # user -> total claimed
        
        # Pool configuration
        self.reward_rate: int = 100  # rewards per second per staked token
        self.total_staked: int = 0
        self.reward_pool: int = 0
    
    def stake(self, user: str, amount: int) -> bool:
        """
        Stake tokens to earn rewards.
        
        Args:
            user: User address
            amount: Amount to stake
            
        Returns:
            bool: True if successful
        """
        if amount <= 0:
            return False
        
        # Claim pending rewards first
        self._claim_rewards(user)
        
        # Update stake
        self.stakes[user] = self.stakes.get(user, 0) + amount
        self.stake_timestamps[user] = int(time.time())
        self.total_staked += amount
        
        return True
    
    def unstake(self, user: str, amount: int) -> bool:
        """
        Unstake tokens and claim rewards.
        
        Args:
            user: User address
            amount: Amount to unstake
            
        Returns:
            bool: True if successful
        """
        user_stake = self.stakes.get(user, 0)
        if amount <= 0 or amount > user_stake:
            return False
        
        # Claim pending rewards first
        self._claim_rewards(user)
        
        # Update stake
        self.stakes[user] = user_stake - amount
        self.total_staked -= amount
        
        # Update timestamp if still staking
        if self.stakes[user] > 0:
            self.stake_timestamps[user] = int(time.time())
        else:
            # Remove user if no stake remaining
            del self.stake_timestamps[user]
        
        return True
    
    def claim_rewards(self, user: str) -> int:
        """
        Claim pending rewards.
        
        Args:
            user: User address
            
        Returns:
            int: Amount of rewards claimed
        """
        return self._claim_rewards(user)
    
    def pending_rewards(self, user: str) -> int:
        """
        Calculate pending rewards for a user.
        
        Args:
            user: User address
            
        Returns:
            int: Pending reward amount
        """
        stake_amount = self.stakes.get(user, 0)
        if stake_amount == 0:
            return 0
        
        stake_time = self.stake_timestamps.get(user, int(time.time()))
        time_staked = int(time.time()) - stake_time
        
        # Calculate rewards: stake_amount * reward_rate * time_staked
        rewards = stake_amount * self.reward_rate * time_staked
        return rewards
    
    def get_stake_info(self, user: str) -> Dict[str, int]:
        """
        Get staking information for a user.
        
        Args:
            user: User address
            
        Returns:
            Dict[str, int]: Staking information
        """
        return {
            "staked_amount": self.stakes.get(user, 0),
            "stake_timestamp": self.stake_timestamps.get(user, 0),
            "pending_rewards": self.pending_rewards(user),
            "total_claimed": self.rewards_claimed.get(user, 0)
        }
    
    def get_pool_info(self) -> Dict[str, int]:
        """
        Get pool information.
        
        Returns:
            Dict[str, int]: Pool statistics
        """
        return {
            "total_staked": self.total_staked,
            "reward_rate": self.reward_rate,
            "reward_pool": self.reward_pool,
            "total_stakers": len(self.stakes)
        }
    
    def set_reward_rate(self, caller: str, new_rate: int) -> bool:
        """
        Set reward rate (only owner).
        
        Args:
            caller: Address calling this function
            new_rate: New reward rate
            
        Returns:
            bool: True if successful
        """
        if caller != self.owner:
            return False
        
        self.reward_rate = new_rate
        return True
    
    def add_rewards(self, caller: str, amount: int) -> bool:
        """
        Add rewards to the pool (only owner).
        
        Args:
            caller: Address calling this function
            amount: Amount to add to reward pool
            
        Returns:
            bool: True if successful
        """
        if caller != self.owner:
            return False
        
        self.reward_pool += amount
        return True
    
    def _claim_rewards(self, user: str) -> int:
        """Internal function to claim rewards."""
        pending = self.pending_rewards(user)
        
        if pending <= 0:
            return 0
        
        if pending > self.reward_pool:
            pending = self.reward_pool
        
        # Update claimed rewards
        self.rewards_claimed[user] = self.rewards_claimed.get(user, 0) + pending
        self.reward_pool -= pending
        
        # Reset stake timestamp
        if user in self.stake_timestamps:
            self.stake_timestamps[user] = int(time.time())
        
        return pending
'''
        
        return ProjectTemplate(
            project_name="{{PROJECT_NAME}}",
            contract_name="{{CONTRACT_NAME}}",
            description="{{DESCRIPTION}}",
            template_type="defi",
            files={
                "contracts/{{CONTRACT_NAME}}.py": defi_content
            }
        )
    
    def list_templates(self) -> Dict[str, str]:
        """
        List available project templates.
        
        Returns:
            Dict[str, str]: Template names and descriptions
        """
        return {
            "basic": "Basic smart contract with storage and counter functionality",
            "token": "ERC-20 style fungible token contract",
            "nft": "ERC-721 style NFT (non-fungible token) contract", 
            "defi": "DeFi staking contract with reward mechanisms"
        }