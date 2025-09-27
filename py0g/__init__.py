"""
py0g: Python-first smart contract CLI for 0G Galileo blockchain

A comprehensive toolkit for developing, compiling, and deploying smart contracts
using Python natively on the 0G AI-optimized blockchain.
"""

__version__ = "0.2.0"
__author__ = "0G Python SDK Team"
__description__ = "Python-first smart contract CLI for 0G Galileo blockchain"

from .compiler import PythonContractCompiler
from .hasher import ProgramHasher
from .prover import ZKProver
from .deployer import ContractDeployer
from .verifier import ContractVerifier

__all__ = [
    "PythonContractCompiler",
    "ProgramHasher", 
    "ZKProver",
    "ContractDeployer",
    "ContractVerifier"
]