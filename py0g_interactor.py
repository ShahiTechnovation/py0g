#!/usr/bin/env python3
"""
Enhanced Universal Contract Interactor for py0g

A comprehensive tool to interact with any smart contract deployed using py0g.
Features improved address handling, better error messages, and enhanced functionality.

Usage:
    python py0g_interactor.py --contract 0x123... --function balance_of --args 0xabc...
    python py0g_interactor.py --scan-contracts  # Scan for all deployed contracts
    python py0g_interactor.py --interactive 0x123...  # Interactive mode
"""

import json
import argparse
import sys
import os
from pathlib import Path
from typing import Dict, Any, List, Optional, Union
from web3 import Web3
from web3.exceptions import ContractLogicError
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.json import JSON
from rich.progress import Progress, SpinnerColumn, TextColumn
import re


class EnhancedContractInteractor:
    """Enhanced universal interactor for py0g deployed contracts."""
    
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
    
    def normalize_address(self, address: str) -> str:
        """Normalize address to proper format."""
        # Remove 0x prefix if present
        if address.startswith('0x'):
            address = address[2:]
        
        # Pad with zeros to make it 40 characters
        address = address.zfill(40)
        
        # Add 0x prefix back
        address = '0x' + address
        
        # Validate length
        if len(address) != 42:
            raise ValueError(f"Invalid address length: {len(address)}")
        
        # Validate hex
        try:
            int(address, 16)
        except ValueError:
            raise ValueError(f"Invalid hex address: {address}")
        
        return Web3.to_checksum_address(address)
    
    def auto_find_abi(self, contract_name: Optional[str] = None) -> List[Dict]:
        """Auto-discover ABI files in the project."""
        search_paths = []
        
        if contract_name:
            # Search for specific contract ABI
            search_paths.extend([
                Path(f"{contract_name}/contracts/artifacts/{contract_name}.abi.json"),
                Path(f"contracts/artifacts/{contract_name}.abi.json"),
                Path(f"artifacts/{contract_name}.abi.json"),
                Path(f"{contract_name}.abi.json"),
            ])
        
        # Search for any ABI files
        for pattern in ["**/*.abi.json", "**/artifacts/*.abi.json"]:
            search_paths.extend(Path(".").glob(pattern))
        
        for abi_path in search_paths:
            if abi_path.exists():
                try:
                    with open(abi_path, 'r') as f:
                        abi = json.load(f)
                        self.console.print(f"[green]📋 Found ABI: {abi_path}[/green]")
                        return abi
                except Exception as e:
                    self.console.print(f"[yellow]⚠️  Failed to load {abi_path}: {e}[/yellow]")
                    continue
        
        return []
    
    def scan_deployed_contracts(self) -> List[Dict[str, str]]:
        """Scan for deployed py0g contracts in the project."""
        contracts = []
        
        # Search for deployment files
        for deployment_file in Path(".").glob("**/artifacts/*_deployment.json"):
            try:
                with open(deployment_file, 'r') as f:
                    deployment = json.load(f)
                    contracts.append({
                        "name": deployment_file.stem.replace("_deployment", ""),
                        "address": deployment.get("contract_address", "Unknown"),
                        "deployment_file": str(deployment_file)
                    })
            except Exception as e:
                continue
        
        # Also check for contracts in common locations
        for contract_dir in ["nii/contracts", "StakingContract/contracts", "we/contracts"]:
            contract_path = Path(contract_dir)
            if contract_path.exists():
                for py_file in contract_path.glob("*.py"):
                    if py_file.stem not in [c["name"] for c in contracts]:
                        # Check if there's an ABI for this contract
                        abi_path = contract_path / "artifacts" / f"{py_file.stem}.abi.json"
                        if abi_path.exists():
                            contracts.append({
                                "name": py_file.stem,
                                "address": "Not deployed",
                                "source_file": str(py_file)
                            })
        
        return contracts
    
    def get_contract_info(self, contract_address: str, abi: List[Dict]) -> Dict[str, Any]:
        """Get comprehensive contract information."""
        try:
            # Normalize address
            address = self.normalize_address(contract_address)
            
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
                'balance': float(self.w3.from_wei(balance, 'ether')),
                'view_functions': view_functions,
                'write_functions': write_functions,
                'total_functions': len(view_functions) + len(write_functions),
                'has_code': len(code) > 0
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
        """Call a contract function with improved error handling."""
        try:
            # Create contract instance
            address = self.normalize_address(contract_address)
            contract = self.w3.eth.contract(address=address, abi=abi)
            
            # Get function
            if not hasattr(contract.functions, function_name):
                available_functions = [item['name'] for item in abi if item.get('type') == 'function']
                self.console.print(f"[red]❌ Function '{function_name}' not found[/red]")
                self.console.print(f"[yellow]Available functions: {', '.join(available_functions)}[/yellow]")
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
                with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}")) as progress:
                    task = progress.add_task("Waiting for confirmation...", total=None)
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
                try:
                    result = func(*call_args).call()
                    return result
                except Exception as call_error:
                    # Try to provide more helpful error messages
                    if "execution reverted" in str(call_error):
                        self.console.print(f"[red]❌ Contract call reverted[/red]")
                        self.console.print(f"[yellow]💡 The contract function rejected the call[/yellow]")
                    elif "stack underflow" in str(call_error):
                        self.console.print(f"[red]❌ EVM stack underflow[/red]")
                        self.console.print(f"[yellow]💡 Contract bytecode may have issues[/yellow]")
                    else:
                        self.console.print(f"[red]❌ Function call failed: {call_error}[/red]")
                    return None
                
        except Exception as e:
            self.console.print(f"[red]❌ Contract interaction failed: {e}[/red]")
            return None
    
    def interactive_mode(self, contract_address: str, abi: List[Dict]) -> None:
        """Enhanced interactive mode."""
        address = self.normalize_address(contract_address)
        
        self.console.print(Panel.fit(
            f"[bold blue]🔧 py0g Interactive Contract Mode[/bold blue]\n"
            f"Contract: {address}\n"
            f"Functions: {len([f for f in abi if f.get('type') == 'function'])}\n"
            f"Type 'help' for commands, 'exit' to quit",
            title="Enhanced Contract Interactor"
        ))
        
        while True:
            try:
                command = input("\n🔧 > ").strip()
                
                if command.lower() in ['exit', 'quit', 'q']:
                    break
                elif command.lower() in ['help', 'h']:
                    self.show_help()
                elif command.lower() in ['list', 'ls']:
                    self.list_functions(abi)
                elif command.lower() in ['info', 'i']:
                    info = self.get_contract_info(address, abi)
                    self.console.print(JSON.from_data(info))
                elif command.lower() in ['scan', 's']:
                    contracts = self.scan_deployed_contracts()
                    self.show_contracts_table(contracts)
                elif command.startswith('call '):
                    parts = command.split()[1:]
                    if parts:
                        func_name = parts[0]
                        args = parts[1:] if len(parts) > 1 else []
                        result = self.call_contract_function(address, abi, func_name, args, False)
                        if result is not None:
                            self.console.print(f"[green]📤 Result: {result}[/green]")
                elif command.startswith('send '):
                    parts = command.split()[1:]
                    if parts:
                        func_name = parts[0]
                        args = parts[1:] if len(parts) > 1 else []
                        result = self.call_contract_function(address, abi, func_name, args, True)
                elif command.startswith('addr '):
                    # Change contract address
                    new_addr = command.split()[1]
                    try:
                        address = self.normalize_address(new_addr)
                        self.console.print(f"[green]✅ Switched to contract: {address}[/green]")
                    except Exception as e:
                        self.console.print(f"[red]❌ Invalid address: {e}[/red]")
                else:
                    self.console.print("[yellow]❓ Unknown command. Type 'help' for available commands.[/yellow]")
                    
            except KeyboardInterrupt:
                break
            except Exception as e:
                self.console.print(f"[red]💥 Error: {e}[/red]")
        
        self.console.print("[dim]👋 Goodbye![/dim]")
    
    def show_help(self):
        """Show help information."""
        help_text = """
[bold]🔧 Available Commands:[/bold]

[cyan]📋 Information:[/cyan]
• [white]list, ls[/white] - Show all contract functions
• [white]info, i[/white] - Show contract information  
• [white]scan, s[/white] - Scan for deployed contracts
• [white]help, h[/white] - Show this help

[cyan]🔧 Function Calls:[/cyan]
• [white]call <function> [args...][/white] - Call read function
• [white]send <function> [args...][/white] - Send write transaction

[cyan]🔄 Navigation:[/cyan]
• [white]addr <address>[/white] - Switch to different contract
• [white]exit, quit, q[/white] - Exit interactive mode

[bold]💡 Examples:[/bold]
• call get_owner
• call balance_of 0x123...
• send transfer 0x456... 1000
• addr 0x789...
"""
        self.console.print(help_text)
    
    def list_functions(self, abi: List[Dict]) -> None:
        """Display functions in enhanced format."""
        view_table = Table(title="📖 View Functions (Read-Only)", show_header=True)
        view_table.add_column("Function", style="cyan", width=20)
        view_table.add_column("Inputs", style="yellow", width=30)
        view_table.add_column("Outputs", style="green", width=15)
        
        write_table = Table(title="✍️ Write Functions (State-Changing)", show_header=True)
        write_table.add_column("Function", style="cyan", width=20)
        write_table.add_column("Inputs", style="yellow", width=30)
        write_table.add_column("Outputs", style="green", width=15)
        
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
    
    def show_contracts_table(self, contracts: List[Dict[str, str]]) -> None:
        """Show deployed contracts in a table."""
        table = Table(title="🚀 Deployed py0g Contracts")
        table.add_column("Contract", style="cyan")
        table.add_column("Address", style="green")
        table.add_column("Status", style="yellow")
        
        for contract in contracts:
            status = "✅ Deployed" if contract["address"] != "Not deployed" else "📝 Source Only"
            table.add_row(contract["name"], contract["address"], status)
        
        self.console.print(table)


def main():
    """Enhanced CLI interface."""
    parser = argparse.ArgumentParser(
        description="Enhanced Universal Contract Interactor for py0g",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
🎯 Examples:

  # Interactive mode (recommended)
  python py0g_interactor.py --interactive 0x123...
  
  # Quick function call
  python py0g_interactor.py --contract 0x123... --function get_owner
  
  # Scan all deployed contracts
  python py0g_interactor.py --scan
  
  # Auto-find ABI and interact
  python py0g_interactor.py --contract 0x123... --auto-abi StakingContract --function get_contract_stats
"""
    )
    
    parser.add_argument('--contract', help='Contract address')
    parser.add_argument('--function', help='Function name to call')
    parser.add_argument('--args', nargs='*', help='Function arguments')
    parser.add_argument('--write', action='store_true', help='Send write transaction')
    parser.add_argument('--key', help='Private key for transactions')
    parser.add_argument('--rpc', default='https://evmrpc-testnet.0g.ai', help='RPC endpoint')
    parser.add_argument('--interactive', metavar='ADDRESS', help='Start interactive mode with contract')
    parser.add_argument('--scan', action='store_true', help='Scan for deployed contracts')
    parser.add_argument('--auto-abi', help='Auto-find ABI for contract name')
    parser.add_argument('--abi-path', help='Direct path to ABI file')
    
    args = parser.parse_args()
    
    # Initialize interactor
    interactor = EnhancedContractInteractor(args.rpc, args.key)
    
    # Handle scan mode
    if args.scan:
        contracts = interactor.scan_deployed_contracts()
        interactor.show_contracts_table(contracts)
        return
    
    # Handle interactive mode
    if args.interactive:
        abi = []
        if args.abi_path:
            with open(args.abi_path, 'r') as f:
                abi = json.load(f)
        elif args.auto_abi:
            abi = interactor.auto_find_abi(args.auto_abi)
        else:
            abi = interactor.auto_find_abi()
        
        if abi:
            interactor.interactive_mode(args.interactive, abi)
        else:
            interactor.console.print("[red]❌ No ABI found. Use --abi-path or --auto-abi[/red]")
        return
    
    # Handle direct function calls
    if args.contract and args.function:
        abi = []
        if args.abi_path:
            with open(args.abi_path, 'r') as f:
                abi = json.load(f)
        elif args.auto_abi:
            abi = interactor.auto_find_abi(args.auto_abi)
        else:
            abi = interactor.auto_find_abi()
        
        if not abi:
            interactor.console.print("[red]❌ No ABI found. Use --abi-path or --auto-abi[/red]")
            return
        
        result = interactor.call_contract_function(
            args.contract, abi, args.function, args.args or [], args.write
        )
        if result is not None and not args.write:
            interactor.console.print(f"[green]📤 Result: {result}[/green]")
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
