# Universal Contract Interactor Guide

The `contract_interactor.py` is a powerful tool to interact with any smart contract deployed using py0g. It automatically finds contract ABIs and provides multiple interaction modes.

## 🚀 Quick Start

### Basic Usage
```bash
# Interactive mode (recommended for exploration)
python contract_interactor.py --contract 0xe41F1AC482e0C0aE66AB1A090Fb1dFfC8FBB224C --contract-path nii/contracts/strk.py --interactive

# Call a read function
python contract_interactor.py --contract 0xe41F1AC482e0C0aE66AB1A090Fb1dFfC8FBB224C --contract-path nii/contracts/strk.py --function balance_of --args 0xD7edbAd4c94663AAE69126453E3B70cdE086a907

# Get contract information
python contract_interactor.py --contract 0xe41F1AC482e0C0aE66AB1A090Fb1dFfC8FBB224C --contract-path nii/contracts/strk.py --info

# List all available functions
python contract_interactor.py --contract 0xe41F1AC482e0C0aE66AB1A090Fb1dFfC8FBB224C --contract-path nii/contracts/strk.py --list-functions
```

## 📋 Command Reference

### Required Arguments
- `--contract ADDRESS` - The deployed contract address

### ABI Loading (choose one)
- `--contract-path PATH` - Path to contract source (auto-finds ABI)
- `--abi-path PATH` - Direct path to ABI JSON file

### Actions (choose one)
- `--interactive` - Start interactive mode
- `--function NAME` - Call specific function
- `--info` - Show contract information
- `--list-functions` - List all functions

### Optional Arguments
- `--args ARG1 ARG2...` - Function arguments
- `--write` - Send write transaction (requires --key)
- `--key PRIVATE_KEY` - Private key for transactions
- `--rpc URL` - Custom RPC endpoint

## 🎯 Interactive Mode

The interactive mode provides a command-line interface for exploring contracts:

```bash
python contract_interactor.py --contract 0x123... --contract-path contract.py --interactive
```

### Interactive Commands
- `list` - Show all functions
- `info` - Show contract information
- `call function_name [args...]` - Call read function
- `send function_name [args...]` - Send write transaction
- `help` - Show help
- `exit` - Exit interactive mode

### Interactive Examples
```
> list                                    # Show all functions
> info                                    # Contract details
> call balance_of 0xD7edbAd4c94663AAE69126453E3B70cdE086a907
> call get_name
> call total_supply
> send transfer 0x456... 1000            # Requires private key
```

## 📊 Examples for Different Contracts

### STRK Token Contract
```bash
# Check token balance
python contract_interactor.py \
  --contract 0xe41F1AC482e0C0aE66AB1A090Fb1dFfC8FBB224C \
  --contract-path nii/contracts/strk.py \
  --function balance_of \
  --args 0xD7edbAd4c94663AAE69126453E3B70cdE086a907

# Get token name
python contract_interactor.py \
  --contract 0xe41F1AC482e0C0aE66AB1A090Fb1dFfC8FBB224C \
  --contract-path nii/contracts/strk.py \
  --function name

# Transfer tokens (requires private key)
python contract_interactor.py \
  --contract 0xe41F1AC482e0C0aE66AB1A090Fb1dFfC8FBB224C \
  --contract-path nii/contracts/strk.py \
  --function transfer \
  --args 0xRecipient... 1000 \
  --write \
  --key 0xYourPrivateKey...
```

### Simple Counter Contract
```bash
# Get current count
python contract_interactor.py \
  --contract 0xb1C3f59A69007e2CE974F46FBb86ca51C869a93C \
  --contract-path nii/contracts/simple_counter.py \
  --function get_count

# Increment counter (requires private key)
python contract_interactor.py \
  --contract 0xb1C3f59A69007e2CE974F46FBb86ca51C869a93C \
  --contract-path nii/contracts/simple_counter.py \
  --function increment \
  --args 0xYourAddress... \
  --write \
  --key 0xYourPrivateKey...
```

### Any Custom Contract
```bash
# Using direct ABI file
python contract_interactor.py \
  --contract 0xYourContract... \
  --abi-path path/to/contract.abi.json \
  --interactive

# Auto-find ABI from contract path
python contract_interactor.py \
  --contract 0xYourContract... \
  --contract-path path/to/contract.py \
  --list-functions
```

## 🔧 Advanced Features

### ABI Auto-Discovery
The interactor automatically searches for ABI files in:
1. `{contract_dir}/artifacts/{contract_name}.abi.json`
2. `artifacts/{contract_name}.abi.json`
3. `nii/contracts/artifacts/{contract_name}.abi.json`
4. `{contract_name}.abi.json`

### Error Handling
- Provides helpful error messages for common issues
- Graceful handling of network failures
- Input validation for addresses and arguments

### Security Features
- Private key validation
- Transaction confirmation waiting
- Gas estimation and usage reporting
- Read/write operation separation

## 🌐 Network Configuration

### Default: 0G Galileo Testnet
- RPC: `https://evmrpc-testnet.0g.ai`
- Chain ID: 16602
- Explorer: https://chainscan-galileo.0g.ai

### Custom Network
```bash
python contract_interactor.py \
  --rpc https://your-custom-rpc.com \
  --contract 0x123... \
  --contract-path contract.py \
  --interactive
```

## 🎯 Use Cases

### Development & Testing
- Test contract functions during development
- Verify deployment correctness
- Debug contract interactions
- Explore contract state

### Production Monitoring
- Monitor contract state
- Check balances and supplies
- Verify transaction results
- Audit contract behavior

### User Interactions
- Provide user-friendly contract interface
- Batch contract operations
- Contract state exploration
- Transaction management

## 🚀 Integration with py0g Workflow

```bash
# 1. Compile contract
py0g compile mycontract.py

# 2. Deploy contract
py0g deploy mycontract.py --key 0x...

# 3. Interact with deployed contract
python contract_interactor.py --contract 0x... --contract-path mycontract.py --interactive
```

This creates a complete development and interaction workflow for py0g smart contracts!
