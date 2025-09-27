# py0g - Python-First Smart Contract Toolkit for 0G Galileo

<div align="center">

![py0g Logo](https://img.shields.io/badge/py0g-v0.2.0-blue?style=for-the-badge&logo=python)
![0G Galileo](https://img.shields.io/badge/0G-Galileo-green?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)

**🐍 Write Smart Contracts in Pure Python | 🚀 Deploy to 0G Galileo | 🤖 AI-Powered Development**

[Quick Start](#quick-start) • [Features](#features) • [Examples](#examples) • [Documentation](#documentation) • [Roadmap](#roadmap)

</div>

## 🌟 **What is py0g?**

**py0g** is a revolutionary Python-first smart contract development toolkit for the **0G Galileo blockchain**. It enables Web2 Python developers to write, compile, and deploy smart contracts using **pure Python** - no Solidity required!

### **🎯 Key Highlights:**
- ✅ **Real EVM Bytecode**: Compiles Python to genuine EVM bytecode (137-349 bytes)
- ✅ **Live Deployments**: Successfully deployed contracts to 0G Galileo testnet
- ✅ **Native Python SDK**: Full token operations (mint, burn, transfer) in Python
- ✅ **AI Integration**: Built-in support for 0G Storage and Compute
- ✅ **Complete CLI**: 10+ commands for full development lifecycle

## 🚀 **Quick Start**

### **Installation**
```bash
# Clone the repository
git clone https://github.com/0g-foundation/py0g.git
cd py0g

# Install dependencies
pip install -r requirements.txt

# Install py0g
pip install -e .
```

### **Create Your First Contract**
```bash
# Initialize a new project
py0g init MyToken
cd MyToken

# Compile the contract
py0g compile contracts/MyToken.py

# Deploy to 0G Galileo testnet
py0g deploy contracts/MyToken.py --rpc https://evmrpc-testnet.0g.ai --key YOUR_PRIVATE_KEY
```

### **Write Python Smart Contracts**
```python
class MyToken:
    """A simple token contract in Python."""
    
    def __init__(self, owner: str, initial_supply: int):
        self.name = "My Token"
        self.symbol = "MTK"
        self.decimals = 18
        self.total_supply = initial_supply
        self.balances = {owner: initial_supply}
    
    def balance_of(self, account: str) -> int:
        """Get token balance."""
        return self.balances.get(account, 0)
    
    def transfer(self, sender: str, recipient: str, amount: int) -> bool:
        """Transfer tokens."""
        if self.balances.get(sender, 0) >= amount:
            self.balances[sender] -= amount
            self.balances[recipient] = self.balances.get(recipient, 0) + amount
            return True
        return False
```

## ✨ **Features**

### **🔧 Complete CLI Toolkit**
```bash
# Project Management
py0g init <project>              # Create new project
py0g template <type> <name>      # Generate from templates

# Development & Compilation
py0g compile <contract>          # Compile to EVM bytecode
py0g debug <contract> <function> # Step-through debugging
py0g analyze <contract>          # Gas optimization analysis

# Blockchain Operations
py0g deploy <contract>           # Deploy to 0G Galileo
py0g run <contract> <function>   # Call contract functions
py0g verify <contract>           # Verify contract integrity

# Utilities
py0g hash <contract>             # Generate program hash
py0g prove <contract>            # Generate ZK proofs
```

### **🤖 AI & 0G Ecosystem Integration**
- **0G Storage**: Store contract metadata and large datasets
- **0G Compute**: Off-chain AI inference and heavy computations
- **AI Oracles**: Built-in templates for AI-powered data feeds
- **ML Contracts**: Deploy and interact with machine learning models

### **📋 Smart Contract Templates**
- **Token Contracts**: ERC-20 style tokens with mint/burn
- **DeFi Protocols**: DEX, lending, staking contracts
- **AI Oracles**: Price prediction and sentiment analysis
- **DAO Governance**: Voting and proposal systems
- **NFT Contracts**: Non-fungible token implementations

### **🛠️ Developer Tools**
- **Visual Debugger**: Step-through execution with gas tracking
- **Gas Analyzer**: Optimization suggestions and cost estimates
- **Security Scanner**: Vulnerability detection and best practices
- **IDE Integration**: VS Code extension (coming soon)

## 📊 **Real-World Results**

### **✅ Proven Track Record**
- **3+ Contracts Deployed** to 0G Galileo testnet
- **250,000+ Gas Used** across live deployments
- **349 Bytes** of real EVM bytecode generated
- **100% Success Rate** on deployments

### **🔗 Live Contract Examples**
| Contract | Address | Type | Gas Used |
|----------|---------|------|----------|
| STRK Token | `0xe41F1AC482e0C0aE66AB1A090Fb1dFfC8FBB224C` | ERC-20 | 125,114 |
| Simple Counter | `0xb1C3f59A69007e2CE974F46FBb86ca51C869a93C` | Utility | 79,992 |

*All contracts are live and verifiable on [0G Galileo Explorer](https://chainscan-galileo.0g.ai)*

## 💡 **Examples**

### **Token Operations (Native Python)**
```python
# Create and interact with tokens in pure Python
from strk import STRKToken

# Deploy token
strk = STRKToken(owner="0x123...", initial_supply=1000000)

# Mint tokens
strk.mint(owner, alice, 50000)  # Mint 50k tokens to Alice

# Transfer tokens
strk.transfer(alice, bob, 25000)  # Alice sends 25k to Bob

# Burn tokens
strk.burn(alice, 10000)  # Alice burns 10k tokens

# Check balances
print(f"Alice: {strk.balance_of(alice)} tokens")
print(f"Total Supply: {strk.total_supply} tokens")
```

### **AI Oracle Contract**
```python
class AIOracle:
    """AI-powered oracle for price predictions."""
    
    async def get_price_prediction(self, asset: str, timeframe: int) -> Dict:
        """Get AI-powered price prediction using 0G Compute."""
        # Submit to 0G Compute for AI inference
        task_id = await self.compute_client.submit_ai_inference_task(
            model_name="crypto_price_lstm_v2",
            input_data={"asset": asset, "timeframe": timeframe}
        )
        
        result = await self.compute_client.get_task_result(task_id)
        return result.result_data
```

### **DeFi DEX Contract**
```python
class SimpleDEX:
    """Automated Market Maker DEX."""
    
    def swap_tokens(self, token_in: str, token_out: str, amount_in: int) -> Tuple[bool, int]:
        """Swap tokens using constant product formula."""
        # Calculate output using AMM formula: (x + dx) * (y - dy) = k
        amount_out = self._calculate_swap_output(token_in, token_out, amount_in)
        
        # Execute swap
        self._update_reserves(token_in, token_out, amount_in, amount_out)
        return True, amount_out
```

## 🏗️ **Architecture**

### **Core Components**

**🔨 Python Compiler (`compiler.py`)**
- Analyzes Python AST to generate real EVM bytecode
- Produces 137-349 bytes of genuine EVM opcodes
- Generates proper ABI with view/nonpayable functions
- Creates comprehensive metadata and artifacts

**🔐 Security & Verification (`verifier.py`, `hasher.py`)**
- Deterministic SHA3-256 program hashing
- Zero-knowledge proof generation (BN254 curve)
- Contract integrity verification
- Reproducible compilation results

**🚀 Deployment Engine (`deployer.py`)**
- Live deployment to 0G Galileo blockchain
- Web3.py integration for transaction management
- Gas estimation and optimization
- Deployment tracking and receipts

**🐛 Developer Tools (`debugger.py`)**
- Step-through contract execution
- Gas usage analysis and optimization
- Security vulnerability scanning
- Performance profiling

**🤖 0G Ecosystem Integration**
- **Storage Client**: Contract metadata and large data storage
- **Compute Client**: AI inference and off-chain processing
- **Template System**: Pre-built contracts for common use cases

## 🛣️ **Roadmap**

### **✅ Completed (v0.2.0)**
- Real EVM bytecode compilation
- Live blockchain deployment
- Native Python SDK
- Complete CLI toolkit
- Contract templates
- Debugging and analysis tools

### **🔄 In Progress (v0.3.0)**
- 0G Storage integration
- 0G Compute integration
- Enhanced AI oracle templates
- IDE extensions (VS Code)
- Advanced security scanning

### **📋 Planned (v0.4.0+)**
- Cross-chain bridges
- Advanced DeFi protocols
- Gaming and NFT templates
- Multi-signature contracts
- Event-driven automation

## 🤝 **Contributing**

We welcome contributions! Here's how you can help:

- **🐛 Bug Reports**: Found an issue? Open a GitHub issue
- **💡 Feature Requests**: Have an idea? We'd love to hear it
- **📝 Documentation**: Help improve our guides and tutorials
- **🔧 Code**: Submit PRs for bug fixes and new features
- **📋 Templates**: Create new contract templates

### **Development Setup**
```bash
# Clone and setup development environment
git clone https://github.com/0g-foundation/py0g.git
cd py0g
pip install -e ".[dev]"

# Run tests
pytest tests/

# Format code
black py0g/
flake8 py0g/
```

## 📚 **Documentation**

- **[Getting Started Guide](docs/getting-started.md)** - Your first py0g contract
- **[API Reference](docs/api-reference.md)** - Complete CLI and SDK documentation
- **[Contract Templates](docs/templates.md)** - Pre-built contract examples
- **[0G Integration](docs/0g-integration.md)** - Storage and Compute usage
- **[Deployment Guide](docs/deployment.md)** - Deploy to 0G Galileo

## 🔗 **Links**

- **GitHub**: [github.com/0g-foundation/py0g](https://github.com/0g-foundation/py0g)
- **0G Foundation**: [0g.ai](https://0g.ai)
- **0G Galileo Explorer**: [chainscan-galileo.0g.ai](https://chainscan-galileo.0g.ai)
- **Documentation**: [docs.py0g.dev](https://docs.py0g.dev)
- **Discord**: [discord.gg/0g](https://discord.gg/0g)

## 📄 **License**

MIT License - see [LICENSE](LICENSE) file for details.

---

<div align="center">

**🚀 Ready to build the future of AI-powered smart contracts with Python?**

[Get Started Now](#quick-start) • [Join Our Community](https://discord.gg/0g) • [Read the Docs](https://docs.py0g.dev)

**Made with ❤️ by the 0G Foundation**

</div>