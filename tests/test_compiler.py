"""
Comprehensive tests for py0g compiler functionality.
"""

import pytest
import tempfile
from pathlib import Path
from py0g.compiler import PythonContractCompiler, CompilerError


class TestPythonContractCompiler:
    """Test suite for Python contract compiler."""
    
    def setup_method(self):
        """Setup test environment."""
        self.compiler = PythonContractCompiler()
        
    def test_compile_simple_contract(self):
        """Test compilation of a simple contract."""
        contract_code = '''
class SimpleContract:
    def __init__(self, owner: str):
        self.owner = owner
        self.value = 0
    
    def get_value(self) -> int:
        return self.value
    
    def set_value(self, caller: str, new_value: int) -> bool:
        if caller == self.owner:
            self.value = new_value
            return True
        return False
'''
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(contract_code)
            f.flush()
            
            result = self.compiler.compile_contract(f.name)
            
            # Verify compilation result
            assert result.bytecode is not None
            assert len(result.bytecode) > 50  # Should be substantial bytecode
            assert len(result.abi) >= 2  # Should have at least 2 functions
            assert result.source_hash is not None
            assert result.metadata is not None
            
            # Clean up
            Path(f.name).unlink()
    
    def test_abi_generation(self):
        """Test ABI generation for different function types."""
        contract_code = '''
class TestContract:
    def __init__(self, owner: str):
        self.owner = owner
    
    def get_owner(self) -> str:
        return self.owner
    
    def balance_of(self, account: str) -> int:
        return 1000
    
    def transfer(self, sender: str, recipient: str, amount: int) -> bool:
        return True
'''
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(contract_code)
            f.flush()
            
            result = self.compiler.compile_contract(f.name)
            
            # Check ABI structure
            abi_functions = {func['name']: func for func in result.abi}
            
            # Verify read-only functions are marked as 'view'
            assert abi_functions['get_owner']['stateMutability'] == 'view'
            assert abi_functions['balance_of']['stateMutability'] == 'view'
            
            # Verify write functions are marked as 'nonpayable'
            assert abi_functions['transfer']['stateMutability'] == 'nonpayable'
            
            # Verify function signatures
            assert len(abi_functions['balance_of']['inputs']) == 1
            assert abi_functions['balance_of']['inputs'][0]['type'] == 'string'
            assert len(abi_functions['transfer']['inputs']) == 3
            
            # Clean up
            Path(f.name).unlink()
    
    def test_bytecode_size_scaling(self):
        """Test that bytecode size scales with contract complexity."""
        simple_contract = '''
class Simple:
    def __init__(self, owner: str):
        self.owner = owner
    
    def get_owner(self) -> str:
        return self.owner
'''
        
        complex_contract = '''
class Complex:
    def __init__(self, owner: str):
        self.owner = owner
        self.balances = {}
        self.allowances = {}
        self.total_supply = 1000000
    
    def balance_of(self, account: str) -> int:
        return self.balances.get(account, 0)
    
    def transfer(self, sender: str, recipient: str, amount: int) -> bool:
        return True
    
    def approve(self, owner: str, spender: str, amount: int) -> bool:
        return True
    
    def allowance(self, owner: str, spender: str) -> int:
        return 0
    
    def mint(self, caller: str, to: str, amount: int) -> bool:
        return True
    
    def burn(self, caller: str, amount: int) -> bool:
        return True
'''
        
        # Compile simple contract
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(simple_contract)
            f.flush()
            simple_result = self.compiler.compile_contract(f.name)
            Path(f.name).unlink()
        
        # Compile complex contract
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(complex_contract)
            f.flush()
            complex_result = self.compiler.compile_contract(f.name)
            Path(f.name).unlink()
        
        # Complex contract should have more bytecode and functions
        assert len(complex_result.bytecode) > len(simple_result.bytecode)
        assert len(complex_result.abi) > len(simple_result.abi)
    
    def test_invalid_contract_compilation(self):
        """Test compilation of invalid contracts."""
        invalid_contract = '''
# This is not a valid contract - no class definition
def some_function():
    return "invalid"
'''
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(invalid_contract)
            f.flush()
            
            # Should handle gracefully
            result = self.compiler.compile_contract(f.name)
            # Should still produce some bytecode (minimal)
            assert result.bytecode is not None
            
            Path(f.name).unlink()
    
    def test_gas_estimation(self):
        """Test gas estimation for different contracts."""
        contract_code = '''
class GasTest:
    def __init__(self, owner: str):
        self.owner = owner
    
    def simple_function(self) -> int:
        return 42
    
    def complex_function(self, a: int, b: int, c: int) -> int:
        # More complex operations should cost more gas
        return a + b + c
'''
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(contract_code)
            f.flush()
            
            result = self.compiler.compile_contract(f.name)
            
            # Should have reasonable gas estimate
            gas_estimate = result.metadata.get('gas_estimate', 0)
            assert gas_estimate > 21000  # Should be more than base transaction cost
            assert gas_estimate < 1000000  # Should be reasonable
            
            Path(f.name).unlink()


if __name__ == "__main__":
    pytest.main([__file__])
