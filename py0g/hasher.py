"""
Program Hash Generator for 0G Ecosystem

Generates deterministic SHA3-256 hashes for compiled contracts with 
reproducible results and contract verification capabilities.
"""

import hashlib
import json
from typing import Dict, Any, Optional
from pathlib import Path
from dataclasses import dataclass
from datetime import datetime


class HashError(Exception):
    """Exception raised during hash generation."""
    pass


@dataclass
class HashResult:
    """Result from program hash generation."""
    program_hash: str
    source_hash: str
    metadata: Dict[str, Any]


class ProgramHasher:
    """
    Deterministic hash generator for compiled contracts.
    
    Ensures reproducible hashes for contract verification and integrity checking.
    """
    
    def __init__(self, output_dir: str = "artifacts"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
    def generate_program_hash(self, source_file: str, bytecode: Optional[bytes] = None) -> HashResult:
        """
        Generate deterministic program hash for a contract.
        
        Args:
            source_file: Path to source file
            bytecode: Optional compiled bytecode
            
        Returns:
            HashResult with program hash and metadata
            
        Raises:
            HashError: If hash generation fails
        """
        try:
            source_path = Path(source_file)
            if not source_path.exists():
                raise HashError(f"Source file not found: {source_file}")
                
            # Read source code
            source_code = source_path.read_text()
            
            # Generate source hash
            source_hash = self._hash_source(source_code)
            
            # Generate program hash
            if bytecode is None:
                # Load bytecode from artifacts if not provided
                bytecode_file = self.output_dir / f"{source_path.stem}.bin"
                if bytecode_file.exists():
                    bytecode = bytecode_file.read_bytes()
                else:
                    # Use source code as fallback
                    bytecode = source_code.encode()
                    
            program_hash = self._hash_program(source_code, bytecode)
            
            # Create metadata
            metadata = {
                "source_file": str(source_path),
                "source_size": len(source_code),
                "bytecode_size": len(bytecode),
                "hash_algorithm": "SHA3-256",
                "compiler_version": "0.2.0",
                "timestamp": datetime.utcnow().isoformat(),
                "deterministic": True
            }
            
            # Save hash metadata
            self._save_hash_metadata(source_path.stem, program_hash, source_hash, metadata)
            
            return HashResult(
                program_hash=program_hash,
                source_hash=source_hash,
                metadata=metadata
            )
            
        except Exception as e:
            raise HashError(f"Hash generation failed: {str(e)}")
    
    def verify_hash(self, source_file: str, expected_hash: str) -> bool:
        """
        Verify that a source file produces the expected hash.
        
        Args:
            source_file: Path to source file
            expected_hash: Expected program hash
            
        Returns:
            True if hash matches, False otherwise
        """
        try:
            result = self.generate_program_hash(source_file)
            return result.program_hash == expected_hash
        except HashError:
            return False
    
    def _hash_source(self, source_code: str) -> str:
        """Generate SHA3-256 hash of source code."""
        # Normalize source code (remove extra whitespace, etc.)
        normalized = self._normalize_source(source_code)
        return hashlib.sha3_256(normalized.encode('utf-8')).hexdigest()
    
    def _hash_program(self, source_code: str, bytecode: bytes) -> str:
        """Generate deterministic program hash from source and bytecode."""
        hasher = hashlib.sha3_256()
        
        # Hash source code first
        normalized_source = self._normalize_source(source_code)
        hasher.update(normalized_source.encode('utf-8'))
        
        # Hash bytecode
        hasher.update(bytecode)
        
        # Add compiler version for determinism
        hasher.update(b"py0g-0.2.0")
        
        return hasher.hexdigest()
    
    def _normalize_source(self, source_code: str) -> str:
        """Normalize source code for consistent hashing."""
        lines = []
        for line in source_code.splitlines():
            # Remove trailing whitespace but preserve indentation
            line = line.rstrip()
            # Skip empty lines for consistency
            if line.strip():
                lines.append(line)
        return '\n'.join(lines)
    
    def _save_hash_metadata(self, name: str, program_hash: str, source_hash: str, metadata: Dict[str, Any]) -> None:
        """Save hash metadata to disk."""
        hash_data = {
            "program_hash": program_hash,
            "source_hash": source_hash,
            "metadata": metadata
        }
        
        hash_file = self.output_dir / f"{name}.hash.json"
        hash_file.write_text(json.dumps(hash_data, indent=2))
    
    def load_hash_metadata(self, contract_name: str) -> Optional[Dict[str, Any]]:
        """Load previously saved hash metadata."""
        hash_file = self.output_dir / f"{contract_name}.hash.json"
        if hash_file.exists():
            return json.loads(hash_file.read_text())
        return None
    
    def hash_contract(self, source_file: str) -> 'HashResult':
        """
        Alias for generate_program_hash for CLI compatibility.
        
        Args:
            source_file: Path to source file
            
        Returns:
            HashResult with program hash and metadata
        """
        return self.generate_program_hash(source_file)
    
    def save_hash(self, hash_result: 'HashResult', output_dir: str) -> str:
        """
        Save hash result to specified directory.
        
        Args:
            hash_result: Hash result to save
            output_dir: Output directory
            
        Returns:
            str: Path to saved hash file
        """
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        # Extract contract name from metadata
        contract_name = hash_result.metadata.get('source_file', 'contract')
        if isinstance(contract_name, str):
            contract_name = Path(contract_name).stem
        
        hash_data = {
            "program_hash": hash_result.program_hash,
            "source_hash": hash_result.source_hash,
            "metadata": hash_result.metadata
        }
        
        hash_file = output_path / f"{contract_name}_hash.json"
        hash_file.write_text(json.dumps(hash_data, indent=2))
        
        return str(hash_file)
    
    def compare_hashes(self, contract1: str, contract2: str) -> Dict[str, Any]:
        """Compare hashes between two contracts."""
        hash1 = self.load_hash_metadata(contract1)
        hash2 = self.load_hash_metadata(contract2)
        
        if not hash1 or not hash2:
            return {"error": "Hash metadata not found for one or both contracts"}
        
        return {
            "contracts": [contract1, contract2],
            "program_hashes_match": hash1["program_hash"] == hash2["program_hash"],
            "source_hashes_match": hash1["source_hash"] == hash2["source_hash"],
            "hash1": hash1["program_hash"],
            "hash2": hash2["program_hash"],
            "metadata_comparison": {
                "compiler_versions_match": hash1["metadata"]["compiler_version"] == hash2["metadata"]["compiler_version"],
                "source_sizes": [hash1["metadata"]["source_size"], hash2["metadata"]["source_size"]],
                "bytecode_sizes": [hash1["metadata"]["bytecode_size"], hash2["metadata"]["bytecode_size"]]
            }
        }


# Convenience function for external use
def generate_program_hash(source_file: str, output_dir: str = "artifacts") -> HashResult:
    """
    Generate program hash for a contract.
    
    Args:
        source_file: Path to source file
        output_dir: Directory for artifacts
        
    Returns:
        HashResult with program hash and metadata
    """
    hasher = ProgramHasher(output_dir)
    return hasher.generate_program_hash(source_file)
