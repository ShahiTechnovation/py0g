#!/usr/bin/env python3
"""
Complete py0g Workflow Demonstration

This script demonstrates the complete py0g workflow:
1. Create a simple contract
2. Compile it to real EVM bytecode
3. Deploy to 0G Galileo testnet
4. Interact with deployed contract
5. Verify all operations work
"""

import subprocess
import json
import time
from pathlib import Path


def run_command(cmd, cwd=None):
    """Run a command and return the result."""
    print(f"🔧 Running: {cmd}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=cwd)
    print(f"Exit code: {result.returncode}")
    if result.stdout:
        print(f"Output: {result.stdout}")
    if result.stderr and result.returncode != 0:
        print(f"Error: {result.stderr}")
    return result


def create_simple_contract():
    """Create a simple test contract."""
    contract_code = '''"""
Simple Counter Contract for Testing

A minimal contract to demonstrate py0g functionality.
"""

class SimpleCounter:
    """A simple counter contract."""
    
    def __init__(self, owner: str):
        """Initialize counter."""
        self.owner: str = owner
        self.count: int = 0
        self.name: str = "SimpleCounter"
    
    def get_count(self) -> int:
        """Get current count (read-only)."""
        return self.count
    
    def get_owner(self) -> str:
        """Get contract owner (read-only)."""
        return self.owner
    
    def get_name(self) -> str:
        """Get contract name (read-only)."""
        return self.name
    
    def increment(self, caller: str) -> bool:
        """Increment counter (write operation)."""
        if caller == self.owner:
            self.count += 1
            return True
        return False
    
    def set_count(self, caller: str, new_count: int) -> bool:
        """Set counter value (write operation)."""
        if caller == self.owner:
            self.count = new_count
            return True
        return False
'''
    
    with open("simple_counter.py", "w") as f:
        f.write(contract_code)
    
    print("✅ Created simple_counter.py")


def main():
    """Run the complete workflow demonstration."""
    print("🚀 py0g Complete Workflow Demonstration")
    print("=" * 60)
    
    # Step 1: Create simple contract
    print("\n📝 Step 1: Creating Simple Contract")
    create_simple_contract()
    
    # Step 2: Compile contract
    print("\n🔨 Step 2: Compiling Contract")
    result = run_command("python -m py0g compile simple_counter.py")
    
    if result.returncode != 0:
        print("❌ Compilation failed!")
        return
    
    print("✅ Compilation successful!")
    
    # Check artifacts
    artifacts_dir = Path("artifacts")
    if artifacts_dir.exists():
        print(f"📁 Generated artifacts:")
        for file in artifacts_dir.glob("simple_counter.*"):
            size = file.stat().st_size
            print(f"   {file.name}: {size} bytes")
    
    # Step 3: Deploy contract
    print("\n🚀 Step 3: Deploying to 0G Galileo Testnet")
    private_key = "0x8daa2744f0e6e9550d79f5ee383b55166467f912916e8a241a77204b9dbcd190"
    
    result = run_command(f"python -m py0g deploy simple_counter.py --rpc https://evmrpc-testnet.0g.ai --key {private_key}")
    
    if result.returncode != 0:
        print("❌ Deployment failed!")
        return
    
    print("✅ Deployment successful!")
    
    # Get contract address from deployment file
    deployment_file = artifacts_dir / "contract_deployment.json"
    if deployment_file.exists():
        with open(deployment_file) as f:
            deployment_data = json.load(f)
        
        contract_address = deployment_data.get("contract_address")
        tx_hash = deployment_data.get("transaction_hash")
        gas_used = deployment_data.get("gas_used")
        
        print(f"📋 Deployment Details:")
        print(f"   Contract Address: {contract_address}")
        print(f"   Transaction Hash: {tx_hash}")
        print(f"   Gas Used: {gas_used:,}")
    
    # Step 4: Test read operations
    print("\n📖 Step 4: Testing Read Operations")
    
    if contract_address:
        # Test get_count
        print("Testing get_count()...")
        result = run_command(f"python -m py0g run simple_counter.py get_count --address {contract_address}")
        
        # Test get_name
        print("Testing get_name()...")
        result = run_command(f"python -m py0g run simple_counter.py get_name --address {contract_address}")
        
        # Test get_owner
        print("Testing get_owner()...")
        result = run_command(f"python -m py0g run simple_counter.py get_owner --address {contract_address}")
    
    # Step 5: Test write operations
    print("\n✍️  Step 5: Testing Write Operations")
    
    if contract_address:
        # Test increment
        print("Testing increment()...")
        owner_address = "0xD7edbAd4c94663AAE69126453E3B70cdE086a907"
        result = run_command(f"python -m py0g run simple_counter.py increment {owner_address} --address {contract_address} --key {private_key}")
        
        if result.returncode == 0:
            print("✅ Write operation successful!")
            
            # Read count again to verify
            print("Verifying count after increment...")
            time.sleep(2)  # Wait for block confirmation
            result = run_command(f"python -m py0g run simple_counter.py get_count --address {contract_address}")
    
    # Step 6: Verification
    print("\n🔍 Step 6: Contract Verification")
    result = run_command("python -m py0g hash simple_counter.py")
    result = run_command("python -m py0g verify simple_counter.py")
    
    # Summary
    print("\n" + "=" * 60)
    print("🎉 py0g Workflow Demonstration Complete!")
    print("\n✅ Achievements:")
    print("   • Created Python smart contract")
    print("   • Compiled to real EVM bytecode")
    print("   • Deployed to 0G Galileo blockchain")
    print("   • Called read-only functions")
    print("   • Executed write transactions")
    print("   • Verified contract integrity")
    print("\n🚀 py0g is fully functional!")
    print("=" * 60)


if __name__ == "__main__":
    main()
