"""
Contract Deployer for 0G Galileo Blockchain

Handles deployment of Python smart contracts to the 0G AI-optimized blockchain
with Web3.py integration, transaction broadcasting, and deployment tracking.
"""

import json
import time
import os
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict
from web3 import Web3
from eth_utils.address import to_checksum_address
import requests


@dataclass
class DeploymentResult:
    """Result of contract deployment."""
    contract_address: str
    transaction_hash: str
    block_number: int
    gas_used: int
    deployment_cost: str
    program_hash: str
    proof_data: str
    metadata: Dict[str, Any]
    timestamp: int


class ContractDeployer:
    """
    Deploys Python smart contracts to 0G Galileo blockchain.
    
    Handles the complete deployment process including:
    - Connection to 0G Galileo testnet
    - Transaction construction and broadcasting
    - Deployment verification and tracking
    - Gas estimation and optimization
    """
    
    def __init__(self, rpc_url: Optional[str] = None, private_key: Optional[str] = None):
        """
        Initialize deployer with 0G Galileo network configuration.
        
        Args:
            rpc_url: 0G RPC endpoint (defaults to Ankr testnet)
            private_key: Private key for signing transactions
        """
        self.rpc_url = rpc_url or "https://evmrpc-testnet.0g.ai"
        self.chain_id = 16602  # 0G Galileo testnet chain ID
        self.explorer_url = "https://chainscan-galileo.0g.ai"
        
        # Initialize Web3 connection
        self.w3 = Web3(Web3.HTTPProvider(self.rpc_url))
        
        # Use provided private key or get from environment
        self.private_key = private_key or os.getenv('ZERO_G_PRIVATE_KEY')
        self.account = None
        
        if self.private_key:
            self.account = self.w3.eth.account.from_key(self.private_key)
    
    def connect(self) -> bool:
        """
        Test connection to 0G Galileo network.
        
        Returns:
            bool: True if connected successfully
        """
        try:
            # Test connection
            latest_block = self.w3.eth.block_number
            chain_id = self.w3.eth.chain_id
            
            if chain_id != self.chain_id:
                print(f"Warning: Connected to chain {chain_id}, expected {self.chain_id}")
            
            print(f"Connected to 0G Galileo - Latest block: {latest_block}")
            return True
        
        except Exception as e:
            print(f"Failed to connect to 0G Galileo: {e}")
            return False
    
    def deploy_contract(self, bytecode: bytes, abi: list, program_hash: str, 
                       proof_data: str, constructor_args: Optional[list] = None) -> DeploymentResult:
        """
        Deploy a contract to 0G Galileo blockchain.
        
        Args:
            bytecode: Compiled contract bytecode
            abi: Contract ABI
            program_hash: Deterministic program hash
            proof_data: ZK proof data
            constructor_args: Constructor arguments
            
        Returns:
            DeploymentResult: Deployment information
        """
        if not self.account:
            raise ValueError("No account configured for deployment")
        
        if not self.connect():
            raise ConnectionError("Failed to connect to 0G Galileo network")
        
        # Prepare constructor data
        constructor_data = b""
        if constructor_args:
            constructor_data = self._encode_constructor_args(abi, constructor_args)
        
        # Create deployment transaction
        deployment_data = bytecode + constructor_data
        
        # Estimate gas
        gas_estimate = self._estimate_deployment_gas(deployment_data)
        
        # Get current gas price (0G has very low fees)
        gas_price = self.w3.eth.gas_price
        
        # Build transaction
        transaction = {
            'nonce': self.w3.eth.get_transaction_count(self.account.address),
            'gasPrice': gas_price,
            'gas': gas_estimate,
            'data': deployment_data.hex() if isinstance(deployment_data, bytes) else deployment_data,
            'chainId': self.chain_id
        }
        
        # Sign and send transaction
        signed_txn = self.w3.eth.account.sign_transaction(transaction, self.private_key)
        tx_hash = self.w3.eth.send_raw_transaction(signed_txn.raw_transaction)
        
        # Wait for transaction receipt
        print(f"Deployment transaction sent: {tx_hash.hex()}")
        print("Waiting for confirmation...")
        
        receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)
        
        if receipt['status'] != 1:
            raise RuntimeError(f"Deployment failed. Transaction: {tx_hash.hex()}")
        
        # Calculate deployment cost
        deployment_cost = receipt['gasUsed'] * gas_price
        deployment_cost_eth = self.w3.from_wei(deployment_cost, 'ether')
        
        # Create deployment metadata
        metadata = {
            "deployer": self.account.address,
            "network": "0G_Galileo_Newton",
            "chain_id": self.chain_id,
            "compiler": "py0g@0.2.0",
            "gas_price": gas_price,
            "explorer_url": f"{self.explorer_url}/tx/{tx_hash.hex()}",
            "contract_size": len(bytecode),
            "proof_included": bool(proof_data)
        }
        
        return DeploymentResult(
            contract_address=receipt['contractAddress'] or '',
            transaction_hash=tx_hash.hex(),
            block_number=receipt['blockNumber'],
            gas_used=receipt['gasUsed'],
            deployment_cost=f"{deployment_cost_eth} A0GI",
            program_hash=program_hash,
            proof_data=proof_data,
            metadata=metadata,
            timestamp=int(time.time())
        )
    
    def simulate_deployment(self, bytecode: bytes, program_hash: str, proof_data: str) -> Dict[str, Any]:
        """
        Simulate contract deployment without actually deploying.
        
        This is useful for testing and cost estimation.
        
        Args:
            bytecode: Contract bytecode
            program_hash: Program hash
            proof_data: ZK proof data
            
        Returns:
            Dict[str, Any]: Simulation results
        """
        # Simulate deployment for testing/demonstration
        simulated_address = self._generate_simulated_address(bytecode, program_hash)
        simulated_tx_hash = self._generate_simulated_tx_hash(program_hash)
        
        # Estimate gas and costs
        gas_estimate = len(bytecode) * 100 + 21000  # Simple estimation
        gas_price = 1000000000  # 1 Gwei (0G has very low fees)
        deployment_cost = gas_estimate * gas_price
        deployment_cost_eth = self.w3.from_wei(deployment_cost, 'ether')
        
        return {
            "simulated": True,
            "contract_address": simulated_address,
            "transaction_hash": simulated_tx_hash,
            "estimated_gas": gas_estimate,
            "estimated_cost": f"{deployment_cost_eth} A0GI",
            "program_hash": program_hash,
            "proof_data": proof_data,
            "network": "0G_Galileo_Newton_Simulation",
            "timestamp": int(time.time()),
            "metadata": {
                "compiler": "py0g@0.2.0",
                "contract_size": len(bytecode),
                "proof_included": bool(proof_data)
            }
        }
    
    def verify_deployment(self, deployment_result: DeploymentResult) -> bool:
        """
        Verify a deployment was successful.
        
        Args:
            deployment_result: Result of previous deployment
            
        Returns:
            bool: True if deployment is verified on chain
        """
        try:
            # Check if contract exists at the address
            code = self.w3.eth.get_code(to_checksum_address(deployment_result.contract_address))
            if len(code) == 0:
                return False
            
            # Verify transaction exists
            try:
                tx_receipt = self.w3.eth.get_transaction_receipt(Web3.to_hex(deployment_result.transaction_hash))
                return tx_receipt['status'] == 1
            except Exception:
                return False
        
        except Exception:
            return False
    
    def get_deployment_info(self, contract_address: str) -> Dict[str, Any]:
        """
        Get information about a deployed contract.
        
        Args:
            contract_address: Address of deployed contract
            
        Returns:
            Dict[str, Any]: Contract information
        """
        try:
            # Validate address
            checksum_address = to_checksum_address(contract_address)
            
            # Get contract code
            code = self.w3.eth.get_code(checksum_address)
            
            if len(code) == 0:
                return {"exists": False, "error": "No contract at address"}
            
            # Get additional info
            balance = self.w3.eth.get_balance(checksum_address)
            
            return {
                "exists": True,
                "address": checksum_address,
                "code_size": len(code),
                "balance": self.w3.from_wei(balance, 'ether'),
                "network": "0G_Galileo",
                "explorer_url": f"{self.explorer_url}/address/{checksum_address}"
            }
        
        except Exception as e:
            return {"exists": False, "error": str(e)}
    
    def _encode_constructor_args(self, abi: list, args: list) -> bytes:
        """Encode constructor arguments."""
        # Find constructor in ABI
        constructor_abi = None
        for item in abi:
            if item.get('type') == 'constructor':
                constructor_abi = item
                break
        
        if not constructor_abi or not args:
            return b""
        
        # Simple encoding (in real implementation, would use proper ABI encoding)
        # For now, just encode as hex
        encoded = b""
        for arg in args:
            if isinstance(arg, str):
                encoded += arg.encode('utf-8').ljust(32, b'\x00')
            elif isinstance(arg, int):
                encoded += arg.to_bytes(32, byteorder='big')
        
        return encoded
    
    def _estimate_deployment_gas(self, deployment_data: bytes) -> int:
        """Estimate gas for contract deployment."""
        # Basic gas estimation for 0G
        base_gas = 21000  # Base transaction cost
        code_gas = len(deployment_data) * 200  # Cost per byte of code
        
        # Add extra gas for contract creation
        creation_gas = 32000
        
        # Add buffer for safety
        total_gas = base_gas + code_gas + creation_gas
        return int(total_gas * 1.2)  # 20% buffer
    
    def _generate_simulated_address(self, bytecode: bytes, program_hash: str) -> str:
        """Generate a simulated contract address for testing."""
        import hashlib
        
        # Create deterministic address based on bytecode and hash
        data = bytecode + program_hash.encode()
        hash_obj = hashlib.sha256(data)
        address_bytes = hash_obj.digest()[:20]
        
        return to_checksum_address(address_bytes)
    
    def _generate_simulated_tx_hash(self, program_hash: str) -> str:
        """Generate a simulated transaction hash."""
        import hashlib
        
        # Create deterministic tx hash
        tx_data = f"{program_hash}_{int(time.time())}"
        tx_hash = hashlib.sha256(tx_data.encode()).hexdigest()
        
        return f"0x{tx_hash}"
    
    def save_deployment(self, deployment_result: DeploymentResult, output_dir: str = "artifacts") -> str:
        """
        Save deployment result to JSON file.
        
        Args:
            deployment_result: Deployment result to save
            output_dir: Output directory
            
        Returns:
            str: Path to saved deployment file
        """
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        # Extract contract name or use address
        contract_name = deployment_result.metadata.get("contract_name", "contract")
        deployment_file = output_path / f"{contract_name}_deployment.json"
        
        # Convert to dictionary and save
        deployment_data = asdict(deployment_result)
        deployment_file.write_text(json.dumps(deployment_data, indent=2))
        
        return str(deployment_file)