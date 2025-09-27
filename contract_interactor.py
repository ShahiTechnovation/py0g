#!/usr/bin/env python3
"""
Universal Contract Interactor for py0g Deployed Contracts

A flexible tool to interact with any smart contract deployed using py0g.
Supports reading contract state, calling functions, and inspecting blockchain data.

Usage:
    python contract_interactor.py --contract 0x123... --function balance_of --args 0xabc...
    python contract_interactor.py --list-functions --contract 0x123...
    python contract_interactor.py --contract-info --contract 0x123...
"""

import json
import argparse
import sys
from pathlib import Path
from typing import Dict, Any, List, Optional, Union
from web3 import Web3
from web3.exceptions import ContractLogicError
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.json import JSON


class UniversalContractInteractor:
    """Universal interactor for any py0g deployed contract."""
    
    def __init__(self, rpc_url: str = "https://evmrpc-testnet.0g.ai", private_key: Optional[str] = None):
        """Initialize blockchain connection."""
        self.console = Console()
        self.rpc_url = rpc_url
        self.private_key = private_key
        
        # Connect to blockchain
        self.w3 = Web3(Web3.HTTPProvider(rpc_url))
        self.chain_id = 16602  # 0G Galileo testnet
        
        if not self.w3.is_connected():
            self.console.print(f"[red]❌ Failed to connect to {rpc_url}[/red]")
            sys.exit(1)
        
        # Setup account if private key provided
        self.account = None
        if private_key:
            try:
                self.account = self.w3.eth.account.from_key(private_key)
                self.w3.eth.default_account = self.account.address
            except Exception as e:
                self.console.print(f"[red]❌ Invalid private key: {e}[/red]")
                sys.exit(1)
        
        self.console.print(f"[green]✅ Connected to 0G Galileo (Block: {self.w3.eth.block_number:,})[/green]")
        if self.account:
            balance = self.w3.eth.get_balance(self.account.address)
            balance_eth = self.w3.from_wei(balance, 'ether')
            self.console.print(f"[cyan]Account: {self.account.address}[/cyan]")
            self.console.print(f"[cyan]Balance: {balance_eth:.6f} A0GI[/cyan]")
    
    def load_contract_abi(self, contract_path: Optional[str] = None, abi_path: Optional[str] = None) -> List[Dict]:
        """Load contract ABI from compiled artifacts or direct ABI file."""
        if abi_path:
            # Load ABI directly from file
            try:
                with open(abi_path, 'r') as f:
                    return json.load(f)
            except Exception as e:
                self.console.print(f"[red]❌ Failed to load ABI from {abi_path}: {e}[/red]")
                return []
        
        if contract_path:
            # Try to find compiled ABI
            contract_name = Path(contract_path).stem
            
            # Search for ABI in common locations
            search_paths = [
                Path(contract_path).parent / "artifacts" / f"{contract_name}.abi.json",
                Path("artifacts") / f"{contract_name}.abi.json",
                Path("nii/contracts/artifacts") / f"{contract_name}.abi.json",
                Path(f"{contract_name}.abi.json")
            ]
            
            for abi_path in search_paths:
                if abi_path.exists():
                    try:
                        with open(abi_path, 'r') as f:
                            return json.load(f)
                    except Exception as e:
                        self.console.print(f"[yellow]⚠️  Failed to load ABI from {abi_path}: {e}[/yellow]")
                        continue
        
        self.console.print(f"[red]❌ No ABI found. Provide --contract-path or --abi-path[/red]")
        return []
    
    def get_contract_info(self, contract_address: str, abi: List[Dict]) -> Dict[str, Any]:
        """Get comprehensive contract information."""
        try:
            # Normalize address
            address = Web3.to_checksum_address(contract_address)
            
            # Get basic contract info
            code = self.w3.eth.get_code(address)
            balance = self.w3.eth.get_balance(address)
            
            # Analyze ABI
            view_functions = []
            write_functions = []
            
            for item in abi:
                if item.get('type') == 'function':
                    func_info = {
                        'name': item['name'],
                        'inputs': len(item.get('inputs', [])),
                        'outputs': len(item.get('outputs', [])),
                        'stateMutability': item.get('stateMutability', 'unknown')
                    }
                    
                    if item.get('stateMutability') in ['view', 'pure']:
                        view_functions.append(func_info)
                    else:
                        write_functions.append(func_info)
            
            return {
                'address': address,
                'code_size': len(code),
                'balance': self.w3.from_wei(balance, 'ether'),
                'view_functions': view_functions,
                'write_functions': write_functions,
                'total_functions': len(view_functions) + len(write_functions)
            }
            
        except Exception as e:
            self.console.print(f"[red]❌ Failed to get contract info: {e}[/red]")
            return {}
    
    def call_contract_function(
        self, 
        contract_address: str, 
        abi: List[Dict], 
        function_name: str, 
        args: List[Any] = None,
        is_write: bool = False
    ) -> Any:
        """Call a contract function (read or write)."""
        try:
            # Create contract instance
            address = Web3.to_checksum_address(contract_address)
            contract = self.w3.eth.contract(address=address, abi=abi)
            
            # Get function
            if not hasattr(contract.functions, function_name):
                self.console.print(f"[red]❌ Function '{function_name}' not found in contract[/red]")
                return None
            
            func = getattr(contract.functions, function_name)
            
            # Prepare arguments
            call_args = args or []
            
            if is_write:
                # Write operation (requires transaction)
                if not self.account:
                    self.console.print(f"[red]❌ Private key required for write operations[/red]")
                    return None
                
                # Build transaction
                transaction = func(*call_args).build_transaction({
                    'from': self.account.address,
                    'nonce': self.w3.eth.get_transaction_count(self.account.address),
                    'gas': 200000,
                    'gasPrice': self.w3.eth.gas_price,
                    'chainId': self.chain_id
                })
                
                # Sign and send transaction
                signed_txn = self.w3.eth.account.sign_transaction(transaction, self.private_key)
                tx_hash = self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)
                
                self.console.print(f"[yellow]⏳ Transaction sent: {tx_hash.hex()}[/yellow]")
                
                # Wait for confirmation
                receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
                
                if receipt.status == 1:
                    self.console.print(f"[green]✅ Transaction successful![/green]")
                    self.console.print(f"[cyan]Gas Used: {receipt.gasUsed:,}[/cyan]")
                    return receipt
                else:
                    self.console.print(f"[red]❌ Transaction failed![/red]")
                    return None
            
            else:
                # Read operation (call)
                result = func(*call_args).call()
                return result
                
        except ContractLogicError as e:
            self.console.print(f"[red]❌ Contract execution failed: {e}[/red]")
            return None
        except Exception as e:
            self.console.print(f"[red]❌ Function call failed: {e}[/red]")
            return None
    
    def list_functions(self, abi: List[Dict]) -> None:
        """Display all available functions in the contract."""
        # Create tables for different function types
        view_table = Table(title="📖 View Functions (Read-Only)")
        view_table.add_column("Function", style="cyan")
        view_table.add_column("Inputs", style="yellow")
        view_table.add_column("Outputs", style="green")
        
        write_table = Table(title="✍️ Write Functions (State-Changing)")
        write_table.add_column("Function", style="cyan")
        write_table.add_column("Inputs", style="yellow")
        write_table.add_column("Outputs", style="green")
        
        for item in abi:
            if item.get('type') == 'function':
                name = item['name']
                inputs = ', '.join([f"{inp.get('name', 'arg')}: {inp['type']}" for inp in item.get('inputs', [])])
                outputs = ', '.join([out['type'] for out in item.get('outputs', [])])
                
                inputs_display = inputs if inputs else "none"
                outputs_display = outputs if outputs else "none"
                
                if item.get('stateMutability') in ['view', 'pure']:
                    view_table.add_row(name, inputs_display, outputs_display)
                else:
                    write_table.add_row(name, inputs_display, outputs_display)
        
        self.console.print(view_table)
        self.console.print()
        self.console.print(write_table)
    
    def interactive_mode(self, contract_address: str, abi: List[Dict]) -> None:
        """Start interactive mode for contract interaction."""
        self.console.print(Panel.fit(
            f"[bold blue]Interactive Contract Mode[/bold blue]\n"
            f"Contract: {contract_address}\n"
            f"Type 'help' for commands, 'exit' to quit",
            title="🔧 py0g Contract Interactor"
        ))
        
        while True:
            try:
                command = input("\n> ").strip()
                
                if command.lower() in ['exit', 'quit']:
                    break
                elif command.lower() == 'help':
                    self.console.print("""
[bold]Available Commands:[/bold]
• [cyan]list[/cyan] - Show all functions
• [cyan]info[/cyan] - Show contract information
• [cyan]call <function> [args...][/cyan] - Call a read function
• [cyan]send <function> [args...][/cyan] - Send a write transaction
• [cyan]help[/cyan] - Show this help
• [cyan]exit[/cyan] - Exit interactive mode

[bold]Examples:[/bold]
• call balance_of 0x123...
• send transfer 0x456... 1000
• call get_name
""")
                elif command.lower() == 'list':
                    self.list_functions(abi)
                elif command.lower() == 'info':
                    info = self.get_contract_info(contract_address, abi)
                    self.console.print(JSON.from_data(info))
                elif command.startswith('call '):
                    parts = command.split()[1:]
                    if parts:
                        func_name = parts[0]
                        args = parts[1:] if len(parts) > 1 else []
                        result = self.call_contract_function(contract_address, abi, func_name, args, False)
                        if result is not None:
                            self.console.print(f"[green]Result: {result}[/green]")
                elif command.startswith('send '):
                    parts = command.split()[1:]
                    if parts:
                        func_name = parts[0]
                        args = parts[1:] if len(parts) > 1 else []
                        result = self.call_contract_function(contract_address, abi, func_name, args, True)
                else:
                    self.console.print("[yellow]Unknown command. Type 'help' for available commands.[/yellow]")
                    
            except KeyboardInterrupt:
                break
            except Exception as e:
                self.console.print(f"[red]Error: {e}[/red]")
        
        self.console.print("[dim]Goodbye![/dim]")


def main():
    """Main CLI interface."""
    parser = argparse.ArgumentParser(
        description="Universal Contract Interactor for py0g deployed contracts",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Interactive mode
  python contract_interactor.py --contract 0x123... --contract-path strk.py --interactive
  
  # Call read function
  python contract_interactor.py --contract 0x123... --abi-path strk.abi.json --function balance_of --args 0xabc...
  
  # Send write transaction
  python contract_interactor.py --contract 0x123... --contract-path strk.py --function transfer --args 0xdef... 1000 --write --key 0x456...
  
  # Get contract info
  python contract_interactor.py --contract 0x123... --contract-path strk.py --info
  
  # List all functions
  python contract_interactor.py --contract 0x123... --abi-path strk.abi.json --list-functions
"""
    )
    
    parser.add_argument('--contract', required=True, help='Contract address')
    parser.add_argument('--contract-path', help='Path to contract source file (for ABI lookup)')
    parser.add_argument('--abi-path', help='Direct path to ABI JSON file')
    parser.add_argument('--function', help='Function name to call')
    parser.add_argument('--args', nargs='*', help='Function arguments')
    parser.add_argument('--write', action='store_true', help='Send write transaction (requires --key)')
    parser.add_argument('--key', help='Private key for write operations')
    parser.add_argument('--rpc', default='https://evmrpc-testnet.0g.ai', help='RPC endpoint')
    parser.add_argument('--interactive', action='store_true', help='Start interactive mode')
    parser.add_argument('--info', action='store_true', help='Show contract information')
    parser.add_argument('--list-functions', action='store_true', help='List all contract functions')
    
    args = parser.parse_args()
    
    # Initialize interactor
    interactor = UniversalContractInteractor(args.rpc, args.key)
    
    # Load ABI
    abi = interactor.load_contract_abi(args.contract_path, args.abi_path)
    if not abi:
        sys.exit(1)
    
    # Execute requested action
    if args.interactive:
        interactor.interactive_mode(args.contract, abi)
    elif args.info:
        info = interactor.get_contract_info(args.contract, abi)
        interactor.console.print(JSON.from_data(info))
    elif args.list_functions:
        interactor.list_functions(abi)
    elif args.function:
        result = interactor.call_contract_function(
            args.contract, abi, args.function, args.args or [], args.write
        )
        if result is not None and not args.write:
            interactor.console.print(f"[green]Result: {result}[/green]")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
