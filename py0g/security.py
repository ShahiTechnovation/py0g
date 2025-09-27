"""
Security analysis and vulnerability detection for py0g contracts.
"""

import ast
from typing import List, Dict, Any
from dataclasses import dataclass
from enum import Enum


class VulnerabilityLevel(Enum):
    """Severity levels for vulnerabilities."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class SecurityIssue:
    """Security issue found in contract."""
    level: VulnerabilityLevel
    title: str
    description: str
    line_number: int
    suggestion: str
    code_snippet: str


class SecurityAnalyzer:
    """Analyzes Python smart contracts for security vulnerabilities."""
    
    def __init__(self):
        """Initialize security analyzer."""
        self.issues: List[SecurityIssue] = []
        self.source_lines: List[str] = []
    
    def analyze_contract(self, source_path: str) -> List[SecurityIssue]:
        """Analyze contract for security issues."""
        self.issues = []
        
        # Read source code
        with open(source_path, 'r') as f:
            source_code = f.read()
            self.source_lines = source_code.split('\n')
        
        # Parse AST
        try:
            tree = ast.parse(source_code)
        except SyntaxError as e:
            self.issues.append(SecurityIssue(
                level=VulnerabilityLevel.HIGH,
                title="Syntax Error",
                description=f"Contract has syntax errors: {e}",
                line_number=e.lineno or 0,
                suggestion="Fix syntax errors before deployment",
                code_snippet=self._get_code_snippet(e.lineno or 0)
            ))
            return self.issues
        
        # Run security checks
        self._check_access_control(tree)
        self._check_input_validation(tree)
        self._check_reentrancy(tree)
        self._check_integer_overflow(tree)
        self._check_dangerous_functions(tree)
        self._check_state_variables(tree)
        
        return self.issues
    
    def _check_access_control(self, tree: ast.AST) -> None:
        """Check for proper access control."""
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # Check if function modifies state without access control
                if self._modifies_state(node) and not self._has_access_control(node):
                    self.issues.append(SecurityIssue(
                        level=VulnerabilityLevel.HIGH,
                        title="Missing Access Control",
                        description=f"Function '{node.name}' modifies state without access control",
                        line_number=node.lineno,
                        suggestion="Add caller verification (e.g., if caller != self.owner)",
                        code_snippet=self._get_code_snippet(node.lineno)
                    ))
    
    def _check_input_validation(self, tree: ast.AST) -> None:
        """Check for input validation."""
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # Check if function parameters are validated
                if len(node.args.args) > 1:  # More than just 'self'
                    has_validation = False
                    for stmt in node.body:
                        if isinstance(stmt, ast.If):
                            # Simple heuristic: if statement might be validation
                            has_validation = True
                            break
                    
                    if not has_validation and self._modifies_state(node):
                        self.issues.append(SecurityIssue(
                            level=VulnerabilityLevel.MEDIUM,
                            title="Missing Input Validation",
                            description=f"Function '{node.name}' doesn't validate input parameters",
                            line_number=node.lineno,
                            suggestion="Add input validation (e.g., amount > 0, address != zero)",
                            code_snippet=self._get_code_snippet(node.lineno)
                        ))
    
    def _check_reentrancy(self, tree: ast.AST) -> None:
        """Check for potential reentrancy vulnerabilities."""
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # Look for external calls followed by state changes
                has_external_call = False
                state_change_after_call = False
                
                for i, stmt in enumerate(node.body):
                    if isinstance(stmt, ast.Call):
                        # Heuristic: function calls might be external
                        has_external_call = True
                    elif has_external_call and isinstance(stmt, ast.Assign):
                        # State change after external call
                        if isinstance(stmt.targets[0], ast.Attribute):
                            state_change_after_call = True
                
                if has_external_call and state_change_after_call:
                    self.issues.append(SecurityIssue(
                        level=VulnerabilityLevel.HIGH,
                        title="Potential Reentrancy",
                        description=f"Function '{node.name}' may be vulnerable to reentrancy",
                        line_number=node.lineno,
                        suggestion="Use checks-effects-interactions pattern",
                        code_snippet=self._get_code_snippet(node.lineno)
                    ))
    
    def _check_integer_overflow(self, tree: ast.AST) -> None:
        """Check for potential integer overflow."""
        for node in ast.walk(tree):
            if isinstance(node, ast.BinOp):
                if isinstance(node.op, (ast.Add, ast.Mult)):
                    self.issues.append(SecurityIssue(
                        level=VulnerabilityLevel.MEDIUM,
                        title="Potential Integer Overflow",
                        description="Arithmetic operation without overflow check",
                        line_number=node.lineno,
                        suggestion="Add overflow checks or use SafeMath equivalent",
                        code_snippet=self._get_code_snippet(node.lineno)
                    ))
    
    def _check_dangerous_functions(self, tree: ast.AST) -> None:
        """Check for dangerous function calls."""
        dangerous_functions = ['eval', 'exec', 'open', 'input', 'print']
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    if node.func.id in dangerous_functions:
                        self.issues.append(SecurityIssue(
                            level=VulnerabilityLevel.CRITICAL,
                            title="Dangerous Function Call",
                            description=f"Use of dangerous function '{node.func.id}'",
                            line_number=node.lineno,
                            suggestion="Remove dangerous function calls from smart contracts",
                            code_snippet=self._get_code_snippet(node.lineno)
                        ))
    
    def _check_state_variables(self, tree: ast.AST) -> None:
        """Check state variable security."""
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                # Check for public sensitive variables
                for stmt in node.body:
                    if isinstance(stmt, ast.FunctionDef) and stmt.name == "__init__":
                        for assign in stmt.body:
                            if isinstance(assign, ast.Assign):
                                for target in assign.targets:
                                    if isinstance(target, ast.Attribute):
                                        var_name = target.attr
                                        if any(sensitive in var_name.lower() 
                                              for sensitive in ['private', 'secret', 'key', 'password']):
                                            self.issues.append(SecurityIssue(
                                                level=VulnerabilityLevel.HIGH,
                                                title="Sensitive Data in State",
                                                description=f"Potentially sensitive variable '{var_name}' stored in state",
                                                line_number=assign.lineno,
                                                suggestion="Avoid storing sensitive data on-chain",
                                                code_snippet=self._get_code_snippet(assign.lineno)
                                            ))
    
    def _modifies_state(self, func_node: ast.FunctionDef) -> bool:
        """Check if function modifies contract state."""
        for stmt in func_node.body:
            if isinstance(stmt, ast.Assign):
                for target in stmt.targets:
                    if isinstance(target, ast.Attribute):
                        if isinstance(target.value, ast.Name) and target.value.id == "self":
                            return True
        return False
    
    def _has_access_control(self, func_node: ast.FunctionDef) -> bool:
        """Check if function has access control."""
        for stmt in func_node.body:
            if isinstance(stmt, ast.If):
                # Look for common access control patterns
                if isinstance(stmt.test, ast.Compare):
                    # Check for self.owner comparison
                    if hasattr(stmt.test.left, 'attr') and 'owner' in str(stmt.test.left.attr):
                        return True
        return False
    
    def _get_code_snippet(self, line_number: int) -> str:
        """Get code snippet around the given line."""
        if not self.source_lines or line_number <= 0:
            return ""
        
        # Get line (1-indexed to 0-indexed)
        line_idx = line_number - 1
        if line_idx < len(self.source_lines):
            return self.source_lines[line_idx].strip()
        
        return ""
    
    def generate_security_report(self, issues: List[SecurityIssue]) -> str:
        """Generate a comprehensive security report."""
        if not issues:
            return "✅ No security issues found!"
        
        # Group issues by severity
        critical = [i for i in issues if i.level == VulnerabilityLevel.CRITICAL]
        high = [i for i in issues if i.level == VulnerabilityLevel.HIGH]
        medium = [i for i in issues if i.level == VulnerabilityLevel.MEDIUM]
        low = [i for i in issues if i.level == VulnerabilityLevel.LOW]
        
        report = "# Security Analysis Report\n\n"
        
        # Summary
        report += f"## Summary\n"
        report += f"- 🔴 Critical: {len(critical)}\n"
        report += f"- 🟠 High: {len(high)}\n"
        report += f"- 🟡 Medium: {len(medium)}\n"
        report += f"- 🟢 Low: {len(low)}\n\n"
        
        # Detailed issues
        for severity, issues_list in [
            ("Critical", critical), ("High", high), 
            ("Medium", medium), ("Low", low)
        ]:
            if issues_list:
                report += f"## {severity} Issues\n\n"
                for i, issue in enumerate(issues_list, 1):
                    report += f"### {i}. {issue.title}\n"
                    report += f"**Line {issue.line_number}**: {issue.description}\n\n"
                    report += f"**Code**: `{issue.code_snippet}`\n\n"
                    report += f"**Suggestion**: {issue.suggestion}\n\n"
        
        return report
