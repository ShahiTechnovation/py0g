#!/usr/bin/env python3
"""
Real Blockchain Interaction with Deployed STRK Contract

This script interacts with the actual deployed STRK contract on 0G Galileo blockchain.
It can read contract functions, call methods, and inspect the real blockchain state.
"""

import json
from web3 import Web3
from typing import Dict, Any, List


class BlockchainContractInteractor:
    """Interact with deployed smart contracts on 0G Galileo blockchain."""
    
    def __init__(self, rpc_url: str = "https://evmrpc-testnet.0g.ai", private_key: str = None):
        """Initialize blockchain connection."""
        self.w3 = Web3(Web3.HTTPProvider(rpc_url))
        self.chain_id = 16602  # 0G Galileo testnet
        
        if private_key:
            self.account = self.w3.eth.account.from_key(private_key)
            self.address = self.account.address
        else:
            self.account = None
            self.address = None
        
        print(f"🌐 Connected to 0G Galileo")
        print(f"   RPC: {rpc_url}")
        print(f"   Chain ID: {self.chain_id}")
        print(f"   Latest Block: {self.w3.eth.block_number}")
        if self.address:
            balance = self.w3.eth.get_balance(self.address)
            print(f"   Account: {self.address}")
            print(f"   Balance: {self.w3.from_wei(balance, 'ether'):.6f} A0GI")
    
    def load_contract(self, contract_address: str, abi_file: str):
        """Load deployed contract using ABI."""
        with open(abi_file, 'r') as f:
            abi = json.load(f)
        
        self.contract_address = Web3.to_checksum_address(contract_address)
        self.contract = self.w3.eth.contract(
            address=self.contract_address,
            abi=abi
        )
        
        print(f"\n📋 Contract Loaded:")
        print(f"   Address: {self.contract_address}")
        print(f"   Functions: {len([f for f in abi if f.get('type') == 'function'])}")
        
        return self.contract
    
    def get_contract_info(self) -> Dict[str, Any]:
        """Get basic contract information."""
        try:
            # Try to get token info (if it's a token contract)
            info = {}
            
            # Check if contract has token functions
            try:
                info['name'] = self.contract.functions.name().call()
                info['symbol'] = self.contract.functions.symbol().call()
                info['decimals'] = self.contract.functions.decimals().call()
                info['total_supply'] = self.contract.functions.total_supply().call()
                info['contract_type'] = 'Token Contract'
            except:
                info['contract_type'] = 'Smart Contract'
            
            # Get contract code size
            code = self.w3.eth.get_code(self.contract_address)
            info['code_size'] = len(code)
            
            return info
        except Exception as e:
            return {'error': str(e)}
    
    def list_functions(self) -> List[Dict[str, Any]]:
        """List all available functions in the contract."""
        functions = []
        
        for item in self.contract.abi:
            if item.get('type') == 'function':
                func_info = {
                    'name': item['name'],
                    'inputs': [f"{inp['type']} {inp['name']}" for inp in item.get('inputs', [])],
                    'outputs': [out['type'] for out in item.get('outputs', [])],
                    'stateMutability': item.get('stateMutability', 'nonpayable')
                }
                functions.append(func_info)
        
        return functions
    
    def call_read_function(self, function_name: str, *args) -> Any:
        """Call a read-only function (no transaction required)."""
        try:
            func = getattr(self.contract.functions, function_name)
            result = func(*args).call()
            return result
        except Exception as e:
            return f"Error: {str(e)}"
    
    def call_write_function(self, function_name: str, *args, gas_limit: int = 200000) -> Dict[str, Any]:
        """Call a state-changing function (requires transaction)."""
        if not self.account:
            return {"error": "Private key required for write operations"}
        
        try:
            # Get function
            func = getattr(self.contract.functions, function_name)
            
            # Build transaction
            transaction = func(*args).build_transaction({
                'from': self.address,
                'gas': gas_limit,
                'gasPrice': self.w3.eth.gas_price,
                'nonce': self.w3.eth.get_transaction_count(self.address),
                'chainId': self.chain_id
            })
            
            # Sign transaction
            signed_txn = self.w3.eth.account.sign_transaction(transaction, self.account.key)
            
            # Send transaction
            tx_hash = self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)
            
            print(f"📤 Transaction sent: {tx_hash.hex()}")
            print("⏳ Waiting for confirmation...")
            
            # Wait for receipt
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
            
            return {
                "success": True,
                "tx_hash": tx_hash.hex(),
                "block_number": receipt.blockNumber,
                "gas_used": receipt.gasUsed,
                "status": receipt.status
            }
            
        except Exception as e:
            return {"error": str(e)}
    
    def get_balance(self, account: str = None) -> int:
        """Get token balance for an account."""
        if account is None:
            account = self.address
        
        try:
            balance = self.contract.functions.balance_of(account).call()
            return balance
        except Exception as e:
            print(f"Error getting balance: {e}")
            return 0
    
    def transfer_tokens(self, to_address: str, amount: int) -> Dict[str, Any]:
        """Transfer tokens to another address."""
        return self.call_write_function("transfer", to_address, amount)
    
    def mint_tokens(self, to_address: str, amount: int) -> Dict[str, Any]:
        """Mint tokens (if caller is authorized)."""
        return self.call_write_function("mint", to_address, amount)
    
    def burn_tokens(self, amount: int) -> Dict[str, Any]:
        """Burn tokens from caller's balance."""
        return self.call_write_function("burn", amount)


def main():
    """Demonstrate real blockchain interaction."""
    print("🚀 Real Blockchain Contract Interaction")
    print("=" * 50)
    
    # Contract details (deployed STRK token)
    CONTRACT_ADDRESS = "0xf121d935c3a2ff6777e86ee35f3285564f6554428"
    ABI_FILE = "artifacts/strk.abi.json"
    PRIVATE_KEY = "0x8daa2744f0e6e9550d79f5ee383b55166467f912916e8a241a77204b9dbcd190"
    
    # Initialize blockchain interactor
    interactor = BlockchainContractInteractor(private_key=PRIVATE_KEY)
    
    # Load the deployed contract
    contract = interactor.load_contract(CONTRACT_ADDRESS, ABI_FILE)
    
    # Get contract information
    print("\n📊 Contract Information:")
    info = interactor.get_contract_info()
    for key, value in info.items():
        print(f"   {key}: {value}")
    
    # List all available functions
    print("\n🔧 Available Functions:")
    functions = interactor.list_functions()
    for i, func in enumerate(functions, 1):
        inputs_str = f"({', '.join(func['inputs'])})" if func['inputs'] else "()"
        outputs_str = f" → {', '.join(func['outputs'])}" if func['outputs'] else ""
        print(f"   {i:2d}. {func['name']}{inputs_str}{outputs_str}")
        print(f"       State: {func['stateMutability']}")
    
    # Demonstrate read operations
    print("\n📖 Read Operations:")
    
    # Check owner balance
    owner_address = interactor.address
    balance = interactor.get_balance(owner_address)
    print(f"   Owner Balance: {balance} wei")
    
    # Try to get token info
    try:
        name = interactor.call_read_function("name")
        symbol = interactor.call_read_function("symbol")
        decimals = interactor.call_read_function("decimals")
        total_supply = interactor.call_read_function("total_supply")
        
        print(f"   Token Name: {name}")
        print(f"   Token Symbol: {symbol}")
        print(f"   Decimals: {decimals}")
        print(f"   Total Supply: {total_supply} wei")
        
        if decimals and isinstance(decimals, int):
            readable_supply = total_supply / (10 ** decimals)
            readable_balance = balance / (10 ** decimals)
            print(f"   Total Supply: {readable_supply:,.2f} {symbol}")
            print(f"   Owner Balance: {readable_balance:,.2f} {symbol}")
    except Exception as e:
        print(f"   Could not read token info: {e}")
    
    # Interactive menu for write operations
    print(f"\n✍️  Write Operations Available:")
    print(f"   1. Mint tokens")
    print(f"   2. Transfer tokens")
    print(f"   3. Burn tokens")
    print(f"   4. Exit")
    
    while True:
        try:
            choice = input(f"\nEnter choice (1-4): ").strip()
            
            if choice == "1":
                # Mint tokens
                to_addr = input("Enter address to mint to (or press Enter for self): ").strip()
                if not to_addr:
                    to_addr = owner_address
                
                amount_str = input("Enter amount to mint (in tokens): ").strip()
                if amount_str:
                    amount = int(float(amount_str) * (10 ** decimals))
                    print(f"\n🪙 Minting {amount_str} tokens to {to_addr[:10]}...")
                    result = interactor.mint_tokens(to_addr, amount)
                    
                    if result.get("success"):
                        print(f"✅ Mint successful!")
                        print(f"   TX: {result['tx_hash']}")
                        print(f"   Gas Used: {result['gas_used']}")
                    else:
                        print(f"❌ Mint failed: {result.get('error')}")
            
            elif choice == "2":
                # Transfer tokens
                to_addr = input("Enter recipient address: ").strip()
                amount_str = input("Enter amount to transfer (in tokens): ").strip()
                
                if to_addr and amount_str:
                    amount = int(float(amount_str) * (10 ** decimals))
                    print(f"\n💸 Transferring {amount_str} tokens to {to_addr[:10]}...")
                    result = interactor.transfer_tokens(to_addr, amount)
                    
                    if result.get("success"):
                        print(f"✅ Transfer successful!")
                        print(f"   TX: {result['tx_hash']}")
                        print(f"   Gas Used: {result['gas_used']}")
                    else:
                        print(f"❌ Transfer failed: {result.get('error')}")
            
            elif choice == "3":
                # Burn tokens
                amount_str = input("Enter amount to burn (in tokens): ").strip()
                
                if amount_str:
                    amount = int(float(amount_str) * (10 ** decimals))
                    print(f"\n🔥 Burning {amount_str} tokens...")
                    result = interactor.burn_tokens(amount)
                    
                    if result.get("success"):
                        print(f"✅ Burn successful!")
                        print(f"   TX: {result['tx_hash']}")
                        print(f"   Gas Used: {result['gas_used']}")
                    else:
                        print(f"❌ Burn failed: {result.get('error')}")
            
            elif choice == "4":
                print("👋 Goodbye!")
                break
            
            else:
                print("❌ Invalid choice. Please enter 1-4.")
                
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")


if __name__ == "__main__":
    main()
