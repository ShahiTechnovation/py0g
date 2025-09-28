# Enhanced Universal Contract Interactor Guide

The `py0g_interactor.py` is an advanced tool for interacting with any smart contract deployed using py0g. It features improved address handling, auto-discovery, and enhanced user experience.

## 🚀 Quick Start

### 1. Scan All Deployed Contracts
```bash
python py0g_interactor.py --scan
```

### 2. Interactive Mode (Recommended)
```bash
# Auto-find ABI and start interactive mode
python py0g_interactor.py --interactive 0x13e745d680286b7df5c680dd4d624976246d3a629 --auto-abi StakingContract

# Use specific ABI file
python py0g_interactor.py --interactive 0xe41F1AC482e0C0aE66AB1A090Fb1dFfC8FBB224C --abi-path nii/contracts/artifacts/strk.abi.json
```

### 3. Direct Function Calls
```bash
# Auto-discover ABI
python py0g_interactor.py --contract 0x13e745d680286b7df5c680dd4d624976246d3a629 --auto-abi StakingContract --function get_owner

# Use specific ABI
python py0g_interactor.py --contract 0xe41F1AC482e0C0aE66AB1A090Fb1dFfC8FBB224C --abi-path nii/contracts/artifacts/strk.abi.json --function balance_of --args 0xD7edbAd4c94663AAE69126453E3B70cdE086a907
```

## 🎯 Enhanced Features

### 🔍 Auto-Discovery
- **Smart ABI Detection**: Automatically finds ABI files in project structure
- **Contract Scanning**: Discovers all deployed py0g contracts
- **Address Normalization**: Handles various address formats automatically

### 🎮 Interactive Mode Commands
```
🔧 > help                    # Show all commands
🔧 > list                    # List contract functions  
🔧 > info                    # Show contract information
🔧 > scan                    # Scan for contracts
🔧 > call get_owner          # Call read function
🔧 > send transfer 0x... 100 # Send transaction
🔧 > addr 0x123...           # Switch contract
🔧 > exit                    # Exit interactive mode
```

### 🛡️ Enhanced Error Handling
- **Helpful Error Messages**: Clear explanations for common issues
- **Address Validation**: Automatic address format correction
- **Function Suggestions**: Shows available functions on errors
- **Network Status**: Real-time blockchain connection info

## 📋 Contract Examples

### Staking Contract
```bash
# Get contract statistics
python py0g_interactor.py --contract 0x13e745d680286b7df5c680dd4d624976246d3a629 --auto-abi StakingContract --function get_contract_stats

# Check pool information
python py0g_interactor.py --contract 0x13e745d680286b7df5c680dd4d624976246d3a629 --auto-abi StakingContract --function get_pool_stats --args 365

# Interactive staking management
python py0g_interactor.py --interactive 0x13e745d680286b7df5c680dd4d624976246d3a629 --auto-abi StakingContract
```

### STRK Token Contract
```bash
# Check token balance
python py0g_interactor.py --contract 0xe41F1AC482e0C0aE66AB1A090Fb1dFfC8FBB224C --abi-path nii/contracts/artifacts/strk.abi.json --function balance_of --args 0xYourAddress

# Interactive token management
python py0g_interactor.py --interactive 0xe41F1AC482e0C0aE66AB1A090Fb1dFfC8FBB224C --abi-path nii/contracts/artifacts/strk.abi.json
```

### Simple Counter Contract
```bash
# Get current count
python py0g_interactor.py --contract 0xb1C3f59A69007e2CE974F46FBb86ca51C869a93C --abi-path nii/contracts/artifacts/simple_counter.abi.json --function get_count
```

## 🔧 Advanced Usage

### Custom RPC Endpoint
```bash
python py0g_interactor.py --rpc https://your-custom-rpc.com --contract 0x123... --function get_owner
```

### Write Transactions
```bash
python py0g_interactor.py --contract 0x123... --function transfer --args 0x456... 1000 --write --key 0xYourPrivateKey
```

### Batch Operations
```bash
# Interactive mode allows multiple operations in sequence
python py0g_interactor.py --interactive 0x123... --auto-abi ContractName
🔧 > call function1
🔧 > call function2 arg1 arg2
🔧 > send function3 arg1
```

## 🎯 Key Improvements Over Basic Interactor

### 1. **Smart Address Handling**
- Automatic address normalization and validation
- Supports various address formats (with/without 0x, different lengths)
- Proper checksum address generation

### 2. **Auto-Discovery System**
- Finds ABI files automatically in project structure
- Scans for deployed contracts across the project
- No need to specify exact paths in most cases

### 3. **Enhanced User Experience**
- Rich console output with colors and formatting
- Progress indicators for transactions
- Helpful error messages and suggestions
- Interactive help system

### 4. **Better Error Handling**
- Specific error messages for common issues
- Function availability checking
- Network connectivity validation
- Transaction status monitoring

### 5. **Comprehensive Functionality**
- Contract scanning and discovery
- Multi-contract management in interactive mode
- Address switching without restart
- Complete transaction lifecycle management

## 🌐 Network Configuration

### Default: 0G Galileo Testnet
- **RPC**: `https://evmrpc-testnet.0g.ai`
- **Chain ID**: 16602
- **Explorer**: https://chainscan-galileo.0g.ai

### Known Deployed Contracts
| Contract | Address | Type |
|----------|---------|------|
| StakingContract | `0x13e745d680286b7df5c680dd4d624976246d3a629` | DeFi Staking |
| STRK Token | `0xe41F1AC482e0C0aE66AB1A090Fb1dFfC8FBB224C` | ERC-20 Token |
| Simple Counter | `0xb1C3f59A69007e2CE974F46FBb86ca51C869a93C` | Utility |

## 🚀 Integration with py0g Workflow

```bash
# Complete development cycle
py0g init MyContract                    # 1. Initialize project
py0g compile MyContract.py              # 2. Compile contract
py0g deploy MyContract.py --key 0x...   # 3. Deploy to blockchain

# Enhanced interaction
python py0g_interactor.py --scan        # 4. Discover deployed contracts
python py0g_interactor.py --interactive 0x... --auto-abi MyContract  # 5. Interact
```

This enhanced interactor provides a complete, professional interface for managing and interacting with py0g smart contracts!
