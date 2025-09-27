# MyProject

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
cd MyProject
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
MyProject/
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
