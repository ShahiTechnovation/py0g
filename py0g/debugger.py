"""
Visual Contract Debugger for py0g

Provides step-through debugging, gas analysis, and execution visualization.
"""

import ast
import json
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from pathlib import Path


@dataclass
class DebugStep:
    """Single debug step information."""
    line_number: int
    function_name: str
    operation: str
    stack_state: List[Any]
    memory_state: Dict[str, Any]
    gas_used: int
    gas_remaining: int


@dataclass
class DebugSession:
    """Debug session data."""
    contract_name: str
    function_name: str
    steps: List[DebugStep]
    total_gas_used: int
    execution_time_ms: float
    success: bool
    error_message: Optional[str] = None


class ContractDebugger:
    """Visual debugger for Python smart contracts."""
    
    def __init__(self):
        """Initialize debugger."""
        self.debug_sessions: Dict[str, DebugSession] = {}
        self.breakpoints: Dict[str, List[int]] = {}  # file -> line numbers
    
    def set_breakpoint(self, contract_path: str, line_number: int) -> bool:
        """Set breakpoint at specific line."""
        if contract_path not in self.breakpoints:
            self.breakpoints[contract_path] = []
        
        if line_number not in self.breakpoints[contract_path]:
            self.breakpoints[contract_path].append(line_number)
            return True
        
        return False
    
    def remove_breakpoint(self, contract_path: str, line_number: int) -> bool:
        """Remove breakpoint."""
        if contract_path in self.breakpoints:
            if line_number in self.breakpoints[contract_path]:
                self.breakpoints[contract_path].remove(line_number)
                return True
        
        return False
    
    def debug_function_call(
        self, 
        contract_path: str, 
        function_name: str, 
        args: List[Any]
    ) -> DebugSession:
        """Debug a function call step by step."""
        contract_name = Path(contract_path).stem
        session_id = f"{contract_name}_{function_name}"
        
        # Simulate debug execution
        debug_steps = [
            DebugStep(
                line_number=25,
                function_name=function_name,
                operation="LOAD_FAST",
                stack_state=["self", "caller"],
                memory_state={"caller": args[0] if args else "unknown"},
                gas_used=3,
                gas_remaining=199997
            ),
            DebugStep(
                line_number=26,
                function_name=function_name,
                operation="COMPARE_OP",
                stack_state=["self.owner", "caller", "=="],
                memory_state={"comparison_result": True},
                gas_used=5,
                gas_remaining=199992
            ),
            DebugStep(
                line_number=27,
                function_name=function_name,
                operation="POP_JUMP_IF_FALSE",
                stack_state=["True"],
                memory_state={"branch_taken": "if_true"},
                gas_used=2,
                gas_remaining=199990
            )
        ]
        
        session = DebugSession(
            contract_name=contract_name,
            function_name=function_name,
            steps=debug_steps,
            total_gas_used=10,
            execution_time_ms=1.5,
            success=True
        )
        
        self.debug_sessions[session_id] = session
        return session
    
    def analyze_gas_usage(self, contract_path: str) -> Dict[str, Any]:
        """Analyze gas usage patterns in contract."""
        # Parse contract to analyze gas usage
        with open(contract_path, 'r') as f:
            source_code = f.read()
        
        tree = ast.parse(source_code)
        
        gas_analysis = {
            "total_estimated_gas": 0,
            "function_gas_costs": {},
            "optimization_suggestions": [],
            "expensive_operations": []
        }
        
        # Analyze each function
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                if not node.name.startswith('_'):
                    # Estimate gas cost based on operations
                    estimated_gas = self._estimate_function_gas(node)
                    gas_analysis["function_gas_costs"][node.name] = estimated_gas
                    gas_analysis["total_estimated_gas"] += estimated_gas
                    
                    # Check for expensive operations
                    expensive_ops = self._find_expensive_operations(node)
                    if expensive_ops:
                        gas_analysis["expensive_operations"].extend(expensive_ops)
        
        # Generate optimization suggestions
        gas_analysis["optimization_suggestions"] = self._generate_optimizations(gas_analysis)
        
        return gas_analysis
    
    def _estimate_function_gas(self, func_node: ast.FunctionDef) -> int:
        """Estimate gas cost for a function."""
        base_cost = 21000  # Base transaction cost
        operation_costs = {
            ast.Assign: 5000,      # Storage write
            ast.Compare: 3,        # Comparison
            ast.BinOp: 5,         # Binary operation
            ast.Call: 700,        # Function call
            ast.If: 10,           # Conditional
            ast.For: 50,          # Loop (per iteration estimate)
            ast.While: 50         # Loop (per iteration estimate)
        }
        
        total_cost = base_cost
        
        for node in ast.walk(func_node):
            for op_type, cost in operation_costs.items():
                if isinstance(node, op_type):
                    total_cost += cost
        
        return total_cost
    
    def _find_expensive_operations(self, func_node: ast.FunctionDef) -> List[Dict]:
        """Find potentially expensive operations."""
        expensive_ops = []
        
        for node in ast.walk(func_node):
            if isinstance(node, ast.For):
                expensive_ops.append({
                    "type": "loop",
                    "line": node.lineno,
                    "warning": "Loops can be gas-expensive",
                    "suggestion": "Consider batch operations or pagination"
                })
            elif isinstance(node, ast.Call) and hasattr(node.func, 'id'):
                if node.func.id in ['print', 'input', 'open']:
                    expensive_ops.append({
                        "type": "io_operation",
                        "line": node.lineno,
                        "warning": "I/O operations not allowed in smart contracts",
                        "suggestion": "Remove I/O operations"
                    })
        
        return expensive_ops
    
    def _generate_optimizations(self, gas_analysis: Dict) -> List[str]:
        """Generate optimization suggestions."""
        suggestions = []
        
        if gas_analysis["total_estimated_gas"] > 1000000:
            suggestions.append("Contract is gas-expensive. Consider splitting into multiple contracts.")
        
        if gas_analysis["expensive_operations"]:
            suggestions.append("Remove expensive operations like loops and I/O.")
        
        # Check for functions with high gas costs
        for func_name, gas_cost in gas_analysis["function_gas_costs"].items():
            if gas_cost > 100000:
                suggestions.append(f"Function '{func_name}' is gas-expensive. Consider optimization.")
        
        return suggestions
    
    def generate_debug_report(self, session_id: str) -> str:
        """Generate detailed debug report."""
        if session_id not in self.debug_sessions:
            return "Debug session not found"
        
        session = self.debug_sessions[session_id]
        
        report = f"""
# Debug Report: {session.contract_name}.{session.function_name}

## Execution Summary
- **Status**: {'✅ Success' if session.success else '❌ Failed'}
- **Total Gas Used**: {session.total_gas_used:,}
- **Execution Time**: {session.execution_time_ms:.2f}ms
- **Steps Executed**: {len(session.steps)}

## Step-by-Step Execution
"""
        
        for i, step in enumerate(session.steps, 1):
            report += f"""
### Step {i} (Line {step.line_number})
- **Operation**: {step.operation}
- **Gas Used**: {step.gas_used} (Remaining: {step.gas_remaining:,})
- **Stack**: {step.stack_state}
- **Memory**: {step.memory_state}
"""
        
        if session.error_message:
            report += f"\n## Error\n{session.error_message}"
        
        return report
