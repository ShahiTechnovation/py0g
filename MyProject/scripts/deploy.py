"""
Deployment script for MyProject

Usage: python scripts/deploy.py
"""

import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from py0g.compiler import PythonContractCompiler
from py0g.hasher import ProgramHasher
from py0g.prover import ZKProver
from py0g.deployer import ContractDeployer


def main():
    """Deploy MyProject to 0G Galileo."""
    contract_path = "contracts/MyProject.py"
    
    print(f"Deploying {contract_path}")
    
    # Check if contract exists
    if not Path(contract_path).exists():
        print(f"Contract file not found: {contract_path}")
        sys.exit(1)
    
    try:
        # 1. Compile contract
        print("Compiling contract...")
        compiler = PythonContractCompiler()
        result = compiler.compile_contract(contract_path)
        compiler.save_artifacts(result, "MyProject", "artifacts")
        print("Compilation complete")
        
        # 2. Generate hash
        print("Generating program hash...")
        hasher = ProgramHasher()
        program_hash = hasher.hash_contract(contract_path)
        hasher.save_hash(program_hash, "artifacts")
        print("Hash generation complete")
        
        # 3. Generate proof
        print("Generating ZK proof...")
        prover = ZKProver()
        proof = prover.generate_proof(contract_path, program_hash.program_hash)
        prover.save_proof(proof, "artifacts")
        print("Proof generation complete")
        
        # 4. Deploy (simulation mode by default)
        print("Simulating deployment...")
        deployer = ContractDeployer()
        simulation = deployer.simulate_deployment(
            result.bytecode, 
            program_hash.program_hash, 
            ""
        )
        
        print("Simulation successful!")
        print(f"  Estimated Address: {simulation['contract_address']}")
        print(f"  Estimated Gas: {simulation['estimated_gas']}")
        print(f"  Estimated Cost: {simulation['estimated_cost']}")
        
    except Exception as e:
        print(f"Deployment failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
