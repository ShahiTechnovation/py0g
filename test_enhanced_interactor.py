#!/usr/bin/env python3
"""
Test script for the enhanced py0g interactor.
"""

import subprocess
import sys

def test_interactor():
    """Test the enhanced interactor functionality."""
    print("🧪 Testing Enhanced py0g Interactor")
    print("=" * 50)
    
    # Test 1: Scan for contracts
    print("\n1. 📡 Scanning for deployed contracts...")
    result = subprocess.run([
        "python", "py0g_interactor.py", "--scan"
    ], capture_output=True, text=True)
    print(result.stdout)
    
    # Test 2: Test staking contract function call
    print("\n2. 🔧 Testing staking contract function call...")
    result = subprocess.run([
        "python", "py0g_interactor.py",
        "--contract", "0x13e745d680286b7df5c680dd4d624976246d3a629",
        "--auto-abi", "StakingContract",
        "--function", "get_owner"
    ], capture_output=True, text=True)
    print(result.stdout)
    if result.stderr:
        print("Stderr:", result.stderr)
    
    # Test 3: Test STRK token contract
    print("\n3. 💰 Testing STRK token contract...")
    result = subprocess.run([
        "python", "py0g_interactor.py",
        "--contract", "0xe41F1AC482e0C0aE66AB1A090Fb1dFfC8FBB224C",
        "--abi-path", "nii/contracts/artifacts/strk.abi.json",
        "--function", "balance_of",
        "--args", "0xD7edbAd4c94663AAE69126453E3B70cdE086a907"
    ], capture_output=True, text=True)
    print(result.stdout)
    if result.stderr:
        print("Stderr:", result.stderr)
    
    # Test 4: Test simple counter contract
    print("\n4. 🔢 Testing simple counter contract...")
    result = subprocess.run([
        "python", "py0g_interactor.py",
        "--contract", "0xb1C3f59A69007e2CE974F46FBb86ca51C869a93C",
        "--abi-path", "nii/contracts/artifacts/simple_counter.abi.json",
        "--function", "get_count"
    ], capture_output=True, text=True)
    print(result.stdout)
    if result.stderr:
        print("Stderr:", result.stderr)
    
    print("\n✅ Enhanced Interactor Test Complete!")

if __name__ == "__main__":
    test_interactor()
