"""

Command-line interface for compiling, deploying, and verifying Python
smart contracts on the 0G AI-optimized blockchain.
"""

import typer
import json
import sys
from typing import Optional, List
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

from .compiler import PythonContractCompiler
from .hasher import ProgramHasher
from .prover import ZKProver
from .deployer import ContractDeployer
from .verifier import ContractVerifier
from .init import ProjectInitializer

# Initialize Typer app
app = typer.Typer(
    name="py0g",
    help="Python-first smart contract CLI for 0G Galileo blockchain",
    no_args_is_help=True
)

# Rich console for beautiful output
console = Console()


@app.command()
def compile(
    contract_path: str = typer.Argument(..., help="Path to Python contract file"),
    output_dir: str = typer.Option("artifacts", "--output", "-o", help="Output directory for artifacts"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose output")
):
    """
    Compile Python contract to 0G-compatible bytecode.
    
    Converts Python smart contracts into bytecode that can be deployed
    to the 0G Galileo blockchain's EVM-compatible execution layer.
    """
    console.print(f"[bold blue][COMPILE] Compiling contract: {contract_path}[/bold blue]")
    
    try:
        compiler = PythonContractCompiler()
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("Compiling contract...", total=None)
            
            # Compile the contract
            result = compiler.compile_contract(contract_path)
            contract_name = Path(contract_path).stem
            
            progress.update(task, description="Saving artifacts...")
            
            # Save artifacts
            saved_files = compiler.save_artifacts(result, contract_name, output_dir)
            
            progress.update(task, description="Complete!", completed=True)
        
        # Display results
        console.print(f"[green]✅ Compilation successful![/green]")
        console.print(f"Contract: [bold]{contract_name}[/bold]")
        console.print(f"Bytecode size: [cyan]{len(result.bytecode)}[/cyan] bytes")
        console.print(f"ABI functions: [cyan]{len(result.abi)}[/cyan]")
        
        if verbose:
            console.print("\n[bold]Generated files:[/bold]")
            for artifact_type, file_path in saved_files.items():
                console.print(f"  {artifact_type}: [dim]{file_path}[/dim]")
                
            console.print("\n[bold]Contract ABI:[/bold]")
            console.print_json(json.dumps(result.abi, indent=2))
    
    except Exception as e:
        console.print(f"[red]❌ Compilation failed: {str(e)}[/red]")
        raise typer.Exit(1)


@app.command()
def hash(
    contract_path: str = typer.Argument(..., help="Path to Python contract file"),
    output_dir: str = typer.Option("artifacts", "--output", "-o", help="Output directory for hash file"),
    verify: Optional[str] = typer.Option(None, "--verify", help="Verify against expected hash")
):
    """
    Generate deterministic program hash for contract verification.
    
    Creates a SHA3-256 hash that uniquely identifies the contract
    and can be used for verification and deployment tracking.
    """
    console.print(f"[bold blue][HASH] Generating program hash: {contract_path}[/bold blue]")
    
    try:
        hasher = ProgramHasher()
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("Generating hash...", total=None)
            
            # Generate hash
            program_hash = hasher.hash_contract(contract_path)
            
            progress.update(task, description="Saving hash file...")
            
            # Save hash
            hash_file = hasher.save_hash(program_hash, output_dir)
            
            progress.update(task, description="Complete!", completed=True)
        
        # Display results
        console.print(f"[green]✅ Hash generated successfully![/green]")
        contract_name = Path(contract_path).stem
        console.print(f"Contract: [bold]{contract_name}[/bold]")
        console.print(f"Program Hash: [cyan]{program_hash.program_hash}[/cyan]")
        console.print(f"Source Hash: [dim]{program_hash.source_hash}[/dim]")
        console.print(f"Saved to: [dim]{hash_file}[/dim]")
        
        # Verify if requested
        if verify:
            if program_hash.program_hash == verify:
                console.print(f"[green]✅ Hash verification: MATCH[/green]")
            else:
                console.print(f"[red]❌ Hash verification: MISMATCH[/red]")
                console.print(f"Expected: [dim]{verify}[/dim]")
                raise typer.Exit(1)
    
    except Exception as e:
        console.print(f"[red]❌ Hash generation failed: {str(e)}[/red]")
        raise typer.Exit(1)


@app.command()
def prove(
    contract_path: str = typer.Argument(..., help="Path to Python contract file"),
    program_hash: Optional[str] = typer.Option(None, "--hash", help="Program hash (auto-generated if not provided)"),
    output_dir: str = typer.Option("artifacts", "--output", "-o", help="Output directory for proof file")
):
    """
    Generate zero-knowledge proof for contract deployment.
    
    Creates a ZK proof that can be used for trustless contract
    verification on the 0G Galileo blockchain.
    """
    console.print(f"[bold blue][PROOF] Generating ZK proof: {contract_path}[/bold blue]")
    
    try:
        prover = ZKProver()
        
        # Generate program hash if not provided
        if not program_hash:
            hasher = ProgramHasher()
            hash_obj = hasher.hash_contract(contract_path)
            program_hash = hash_obj.program_hash
            console.print(f"Generated program hash: [dim]{program_hash}[/dim]")
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("Generating proof...", total=None)
            
            # Generate proof
            proof = prover.generate_proof(program_hash, contract_path)
            
            progress.update(task, description="Saving proof file...")
            
            # Save proof
            proof_file = prover.save_proof(proof, output_dir)
            
            progress.update(task, description="Complete!", completed=True)
        
        # Display results
        console.print(f"[green]✅ Proof generated successfully![/green]")
        console.print(f"Contract: [bold]{proof.metadata['contract_name']}[/bold]")
        console.print(f"Proof Type: [cyan]{proof.proof_type}[/cyan]")
        console.print(f"Circuit Size: [cyan]{proof.metadata['circuit_size']}[/cyan] constraints")
        console.print(f"Proving Time: [cyan]{proof.metadata['proving_time_ms']}[/cyan] ms")
        console.print(f"Saved to: [dim]{proof_file}[/dim]")
    
    except Exception as e:
        console.print(f"[red]❌ Proof generation failed: {str(e)}[/red]")
        raise typer.Exit(1)


@app.command()
def deploy(
    contract_path: str = typer.Argument(..., help="Path to Python contract file"),
    rpc_url: Optional[str] = typer.Option(None, "--rpc", help="0G RPC endpoint"),
    private_key: Optional[str] = typer.Option(None, "--key", help="Private key for deployment (or set ZERO_G_PRIVATE_KEY env var)"),
    simulate: bool = typer.Option(False, "--simulate", help="Simulate deployment without sending transaction"),
    artifacts_dir: str = typer.Option("artifacts", "--artifacts", help="Artifacts directory")
):
    """
    Deploy Python contract to 0G Galileo blockchain.
    
    Deploys compiled contracts to the 0G AI-optimized blockchain
    with automatic gas estimation and transaction broadcasting.
    """
    console.print(f"[bold blue]🚀 Deploying contract: {contract_path}[/bold blue]")
    
    try:
        # Load artifacts
        contract_name = Path(contract_path).stem
        artifacts_path = Path(artifacts_dir)
        
        # Load bytecode
        bytecode_file = artifacts_path / f"{contract_name}.bin"
        if not bytecode_file.exists():
            console.print(f"[red]❌ Bytecode not found. Run 'py0g compile {contract_path}' first.[/red]")
            raise typer.Exit(1)
        
        bytecode = bytecode_file.read_bytes()
        
        # Load ABI
        abi_file = artifacts_path / f"{contract_name}.abi.json"
        abi = json.loads(abi_file.read_text()) if abi_file.exists() else []
        
        # Load hash
        hash_file = artifacts_path / f"{contract_name}_hash.json"
        program_hash = ""
        if hash_file.exists():
            hash_data = json.loads(hash_file.read_text())
            program_hash = hash_data.get("program_hash", "")
        
        # Load proof
        proof_file = artifacts_path / f"{contract_name}_proof.json"
        proof_data = ""
        if proof_file.exists():
            proof_data = proof_file.read_text()
        
        # Initialize deployer
        deployer = ContractDeployer(rpc_url, private_key)
        
        if simulate:
            # Simulate deployment
            console.print("[yellow]🔍 Simulating deployment...[/yellow]")
            result = deployer.simulate_deployment(bytecode, program_hash, proof_data)
            
            console.print(f"[green]✅ Simulation successful![/green]")
            console.print(f"Estimated Address: [cyan]{result['contract_address']}[/cyan]")
            console.print(f"Estimated Gas: [cyan]{result['estimated_gas']}[/cyan]")
            console.print(f"Estimated Cost: [cyan]{result['estimated_cost']}[/cyan]")
            
        else:
            # Real deployment - check if we have a private key available
            deployer_check = ContractDeployer(rpc_url, private_key)
            if not deployer_check.private_key:
                console.print("[red]❌ Private key required for real deployment. Use --key flag or set ZERO_G_PRIVATE_KEY environment variable.[/red]")
                raise typer.Exit(1)
            
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console
            ) as progress:
                task = progress.add_task("Deploying to 0G Galileo...", total=None)
                
                # Deploy contract
                result = deployer.deploy_contract(bytecode, abi, program_hash, proof_data)
                
                progress.update(task, description="Saving deployment info...")
                
                # Save deployment result
                deployment_file = deployer.save_deployment(result, artifacts_dir)
                
                progress.update(task, description="Complete!", completed=True)
            
            console.print(f"[green]✅ Deployment successful![/green]")
            console.print(f"Contract Address: [cyan]{result.contract_address}[/cyan]")
            console.print(f"Transaction Hash: [cyan]{result.transaction_hash}[/cyan]")
            console.print(f"Gas Used: [cyan]{result.gas_used}[/cyan]")
            console.print(f"Cost: [cyan]{result.deployment_cost}[/cyan]")
            console.print(f"Explorer: [link]{result.metadata['explorer_url']}[/link]")
    
    except Exception as e:
        console.print(f"[red]❌ Deployment failed: {str(e)}[/red]")
        raise typer.Exit(1)


@app.command()
def verify(
    contract_path: str = typer.Argument(..., help="Path to Python contract file"),
    program_hash: Optional[str] = typer.Option(None, "--hash", help="Expected program hash"),
    artifacts_dir: str = typer.Option("artifacts", "--artifacts", help="Artifacts directory"),
    report: bool = typer.Option(False, "--report", help="Generate detailed verification report")
):
    """
    Verify contract compilation and proof validity.
    
    Recompiles the contract and compares against the expected hash
    to ensure deterministic compilation and contract integrity.
    """
    console.print(f"[bold blue]🔍 Verifying contract: {contract_path}[/bold blue]")
    
    try:
        verifier = ContractVerifier()
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("Verifying contract...", total=None)
            
            # Verify contract
            if program_hash:
                result = verifier.verify_contract(contract_path, program_hash)
            else:
                result = verifier.verify_from_artifacts(contract_path, artifacts_dir)
            
            progress.update(task, description="Complete!", completed=True)
        
        # Display results
        if result.verified:
            console.print(f"[green]✅ Verification successful![/green]")
        else:
            console.print(f"[red]❌ Verification failed![/red]")
        
        console.print(f"Contract: [bold]{result.contract_name}[/bold]")
        console.print(f"Hash Match: {'✅' if result.source_matches else '❌'}")
        console.print(f"Proof Valid: {'✅' if result.proof_valid else '❌'}")
        
        if report:
            verification_report = verifier.generate_verification_report(result)
            console.print("\n[bold]Detailed Verification Report:[/bold]")
            console.print(verification_report)
    
    except Exception as e:
        console.print(f"[red]❌ Verification failed: {str(e)}[/red]")
        raise typer.Exit(1)


@app.command()
def init(
    project_name: str = typer.Argument(..., help="Name of the new project"),
    template: str = typer.Option("basic", "--template", "-t", help="Project template (basic, token, nft, defi)"),
    directory: Optional[str] = typer.Option(None, "--directory", "-d", help="Target directory (defaults to project name)")
):
    """
    Initialize a new py0g smart contract project.
    
    Creates a new Python smart contract project with proper structure,
    example contracts, configuration files, and development setup.
    """
    console.print(f"[bold blue]🚀 Initializing new py0g project: {project_name}[/bold blue]")
    
    try:
        initializer = ProjectInitializer()
        
        # List available templates if user requests it
        if template == "list":
            console.print("\n[bold]Available Templates:[/bold]")
            templates = initializer.list_templates()
            
            template_table = Table(show_header=True, header_style="bold magenta")
            template_table.add_column("Template", style="cyan")
            template_table.add_column("Description", style="dim")
            
            for tmpl_name, description in templates.items():
                template_table.add_row(tmpl_name, description)
            
            console.print(template_table)
            return
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("Creating project structure...", total=None)
            
            # Initialize project
            project_path = initializer.init_project(project_name, template, directory)
            
            progress.update(task, description="Generating template files...")
            progress.update(task, description="Creating configuration...")
            progress.update(task, description="Complete!", completed=True)
        
        # Display results
        console.print(f"[green]✅ Project initialized successfully![/green]")
        console.print(f"Project: [bold]{project_name}[/bold]")
        console.print(f"Template: [cyan]{template}[/cyan]")
        console.print(f"Location: [dim]{project_path}[/dim]")
        
        # Show next steps
        console.print("\n[bold]Next Steps:[/bold]")
        console.print(f"1. Navigate to your project: [cyan]cd {project_name}[/cyan]")
        console.print(f"2. Compile your contract: [cyan]py0g compile contracts/*.py[/cyan]")
        console.print(f"3. Test deployment: [cyan]py0g deploy contracts/*.py --simulate[/cyan]")
        console.print(f"4. Read the README.md for detailed instructions")
        
        # Show project structure
        console.print(f"\n[bold]Project Structure:[/bold]")
        structure_table = Table(show_header=False, box=None, padding=(0, 2))
        structure_table.add_column("", style="dim")
        structure_table.add_column("", style="cyan")
        
        structure_table.add_row("[DIR]", f"{project_name}/")
        structure_table.add_row("  [FILE]", "contracts/        # Python smart contracts")
        structure_table.add_row("  [DIR]", "artifacts/        # Compiled bytecode")
        structure_table.add_row("  [TEST]", "tests/           # Contract tests")
        structure_table.add_row("  [SCRIPT]", "scripts/         # Deployment scripts")
        structure_table.add_row("  [DOCS]", "docs/            # Documentation")
        structure_table.add_row("  [CONFIG]", "py0g.config.json # Configuration")
        structure_table.add_row("  [README]", "README.md        # Getting started")
        
        console.print(structure_table)
        
    except ValueError as e:
        console.print(f"[red]❌ {str(e)}[/red]")
        if "already exists" in str(e):
            console.print("[yellow]💡 Use --directory flag to specify a different location[/yellow]")
        elif "Unknown template" in str(e):
            console.print("[yellow]💡 Use 'py0g init --template list' to see available templates[/yellow]")
        raise typer.Exit(1)
        
    except Exception as e:
        console.print(f"[red]❌ Project initialization failed: {str(e)}[/red]")
        raise typer.Exit(1)


@app.command()
def run(
    contract_path: str = typer.Argument(..., help="Path to deployed contract"),
    function_name: str = typer.Argument(..., help="Function name to call"),
    args: Optional[List[str]] = typer.Argument(None, help="Function arguments"),
    rpc_url: Optional[str] = typer.Option("https://evmrpc-testnet.0g.ai", "--rpc", help="0G RPC endpoint"),
    private_key: Optional[str] = typer.Option(None, "--key", help="Private key for write operations"),
    contract_address: Optional[str] = typer.Option(None, "--address", help="Contract address"),
    artifacts_dir: str = typer.Option("artifacts", "--artifacts", help="Artifacts directory")
):
    """
    Call functions on deployed smart contracts.
    
    Interact with deployed contracts by calling their functions
    directly from the command line with real blockchain state.
    """
    console.print(f"[bold blue]🔧 Calling function: {function_name}[/bold blue]")
    
    try:
        from web3 import Web3
        import json
        from pathlib import Path
        
        # Load contract artifacts
        contract_name = Path(contract_path).stem
        artifacts_path = Path(artifacts_dir)
        
        # Load ABI
        abi_file = artifacts_path / f"{contract_name}.abi.json"
        if not abi_file.exists():
            console.print(f"[red]❌ ABI file not found: {abi_file}[/red]")
            console.print(f"[yellow]💡 Run 'py0g compile {contract_path}' first[/yellow]")
            raise typer.Exit(1)
        
        abi = json.loads(abi_file.read_text())
        
        # Get contract address
        if not contract_address:
            deployment_file = artifacts_path / "contract_deployment.json"
            if deployment_file.exists():
                deployment_data = json.loads(deployment_file.read_text())
                contract_address = deployment_data.get("contract_address")
        
        if not contract_address:
            console.print(f"[red]❌ Contract address not found[/red]")
            console.print(f"[yellow]💡 Use --address flag or deploy contract first[/yellow]")
            raise typer.Exit(1)
        
        # Connect to blockchain
        w3 = Web3(Web3.HTTPProvider(rpc_url))
        if not w3.is_connected():
            console.print(f"[red]❌ Failed to connect to {rpc_url}[/red]")
            raise typer.Exit(1)
        
        console.print(f"[green]✅ Connected to 0G Galileo (Block: {w3.eth.block_number})[/green]")
        
        # Load contract
        if not contract_address.startswith('0x'):
            contract_address = '0x' + contract_address
        contract_address = Web3.to_checksum_address(contract_address)
        contract = w3.eth.contract(address=contract_address, abi=abi)
        
        console.print(f"[cyan]Contract: {contract_address}[/cyan]")
        console.print(f"[cyan]Function: {function_name}[/cyan]")
        
        # Parse arguments
        parsed_args = []
        if args:
            for arg in args:
                # Try to parse as int, then string
                try:
                    parsed_args.append(int(arg))
                except ValueError:
                    parsed_args.append(arg)
        
        console.print(f"[cyan]Arguments: {parsed_args}[/cyan]")
        
        # Check if function exists
        if not hasattr(contract.functions, function_name):
            console.print(f"[red]❌ Function '{function_name}' not found in contract[/red]")
            
            # List available functions
            functions = [item['name'] for item in abi if item.get('type') == 'function']
            console.print(f"[yellow]Available functions: {', '.join(functions)}[/yellow]")
            raise typer.Exit(1)
        
        # Get function
        func = getattr(contract.functions, function_name)
        
        # Determine if it's a read or write function
        func_abi = next((item for item in abi if item.get('name') == function_name), {})
        is_read_only = func_abi.get('stateMutability') in ['view', 'pure']
        
        if is_read_only:
            # Read-only function call
            console.print(f"[blue]📖 Calling read-only function...[/blue]")
            result = func(*parsed_args).call()
            
            console.print(f"[green]✅ Function call successful![/green]")
            console.print(f"[bold]Result: {result}[/bold]")
            
        else:
            # Write function - requires transaction
            if not private_key:
                console.print(f"[red]❌ Private key required for write operations[/red]")
                console.print(f"[yellow]💡 Use --key flag or set ZERO_G_PRIVATE_KEY env var[/yellow]")
                raise typer.Exit(1)
            
            console.print(f"[blue]✍️  Sending transaction...[/blue]")
            
            # Setup account
            account = w3.eth.account.from_key(private_key)
            
            # Build transaction
            transaction = func(*parsed_args).build_transaction({
                'from': account.address,
                'gas': 200000,
                'gasPrice': w3.eth.gas_price,
                'nonce': w3.eth.get_transaction_count(account.address),
                'chainId': 16602
            })
            
            # Sign and send
            signed_txn = w3.eth.account.sign_transaction(transaction, private_key)
            tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
            
            console.print(f"[yellow]⏳ Transaction sent: {tx_hash.hex()}[/yellow]")
            console.print(f"[yellow]Waiting for confirmation...[/yellow]")
            
            # Wait for receipt
            receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
            
            if receipt.status == 1:
                console.print(f"[green]✅ Transaction successful![/green]")
                console.print(f"[cyan]Block: {receipt.blockNumber}[/cyan]")
                console.print(f"[cyan]Gas Used: {receipt.gasUsed}[/cyan]")
            else:
                console.print(f"[red]❌ Transaction failed![/red]")
                raise typer.Exit(1)
    
    except ImportError:
        console.print(f"[red]❌ web3 library not installed[/red]")
        console.print(f"[yellow]💡 Run: pip install web3[/yellow]")
        raise typer.Exit(1)
    
    except Exception as e:
        error_msg = str(e)
        
        # Provide helpful error messages for common issues
        if "stack underflow" in error_msg.lower():
            console.print(f"[red]❌ Contract execution failed: EVM stack underflow[/red]")
            console.print(f"[yellow]💡 This usually means the contract bytecode has issues[/yellow]")
            console.print(f"[yellow]💡 Try recompiling the contract or check function parameters[/yellow]")
        elif "unknown format" in error_msg.lower():
            console.print(f"[red]❌ Invalid contract address format[/red]")
            console.print(f"[yellow]💡 Contract address should be 40 hex characters (with or without 0x prefix)[/yellow]")
        elif "connection" in error_msg.lower():
            console.print(f"[red]❌ Failed to connect to blockchain[/red]")
            console.print(f"[yellow]💡 Check your internet connection and RPC endpoint[/yellow]")
        elif "insufficient funds" in error_msg.lower():
            console.print(f"[red]❌ Insufficient funds for transaction[/red]")
            console.print(f"[yellow]💡 Make sure your account has enough A0GI for gas fees[/yellow]")
        else:
            console.print(f"[red]❌ Function call failed: {error_msg}[/red]")
        
        # Show debug information in verbose mode
        if "--verbose" in sys.argv:
            import traceback
            console.print(f"[dim]Debug traceback:[/dim]")
            console.print(f"[dim]{traceback.format_exc()}[/dim]")
        
        raise typer.Exit(1)


@app.command()
def debug(
    contract_path: str = typer.Argument(..., help="Path to contract file"),
    function_name: str = typer.Argument(..., help="Function to debug"),
    args: Optional[List[str]] = typer.Argument(None, help="Function arguments"),
    breakpoints: Optional[List[int]] = typer.Option(None, "--breakpoint", "-b", help="Set breakpoints at line numbers")
):
    """
    Debug smart contract execution step-by-step.
    
    Provides detailed execution analysis, gas usage tracking,
    and step-through debugging capabilities.
    """
    console.print(f"[bold blue]🐛 Debugging: {contract_path}.{function_name}[/bold blue]")
    
    try:
        from .debugger import ContractDebugger
        
        debugger = ContractDebugger()
        
        # Set breakpoints if provided
        if breakpoints:
            for line_num in breakpoints:
                debugger.set_breakpoint(contract_path, line_num)
                console.print(f"[yellow]🔴 Breakpoint set at line {line_num}[/yellow]")
        
        # Parse arguments
        parsed_args = []
        if args:
            for arg in args:
                try:
                    parsed_args.append(int(arg))
                except ValueError:
                    parsed_args.append(arg)
        
        # Run debug session
        session = debugger.debug_function_call(contract_path, function_name, parsed_args)
        
        # Display results
        console.print(f"[green]✅ Debug session completed![/green]")
        console.print(f"Steps executed: [cyan]{len(session.steps)}[/cyan]")
        console.print(f"Total gas used: [cyan]{session.total_gas_used:,}[/cyan]")
        console.print(f"Execution time: [cyan]{session.execution_time_ms:.2f}ms[/cyan]")
        
        # Show step details
        for i, step in enumerate(session.steps, 1):
            console.print(f"\n[bold]Step {i} (Line {step.line_number}):[/bold]")
            console.print(f"  Operation: {step.operation}")
            console.print(f"  Gas: {step.gas_used} (Remaining: {step.gas_remaining:,})")
            console.print(f"  Stack: {step.stack_state}")
        
        # Generate report
        session_id = f"{Path(contract_path).stem}_{function_name}"
        report = debugger.generate_debug_report(session_id)
        
        # Save report
        report_file = Path("debug_report.md")
        report_file.write_text(report)
        console.print(f"\n[dim]Debug report saved to: {report_file}[/dim]")
        
    except Exception as e:
        console.print(f"[red]❌ Debug failed: {str(e)}[/red]")
        raise typer.Exit(1)


@app.command()
def analyze(
    contract_path: str = typer.Argument(..., help="Path to contract file"),
    output_format: str = typer.Option("table", "--format", help="Output format: table, json, markdown")
):
    """
    Analyze contract for gas optimization and security issues.
    
    Provides detailed analysis of gas usage patterns,
    security vulnerabilities, and optimization suggestions.
    """
    console.print(f"[bold blue]🔍 Analyzing: {contract_path}[/bold blue]")
    
    try:
        from .debugger import ContractDebugger
        
        debugger = ContractDebugger()
        analysis = debugger.analyze_gas_usage(contract_path)
        
        if output_format == "table":
            # Display as table
            table = Table(title="Gas Analysis Report")
            table.add_column("Function", style="cyan")
            table.add_column("Estimated Gas", style="magenta")
            table.add_column("Optimization", style="green")
            
            for func_name, gas_cost in analysis["function_gas_costs"].items():
                optimization = "✅ Efficient" if gas_cost < 50000 else "⚠️ Review"
                table.add_row(func_name, f"{gas_cost:,}", optimization)
            
            console.print(table)
            
            # Show optimization suggestions
            if analysis["optimization_suggestions"]:
                console.print("\n[bold yellow]💡 Optimization Suggestions:[/bold yellow]")
                for suggestion in analysis["optimization_suggestions"]:
                    console.print(f"  • {suggestion}")
            
            # Show expensive operations
            if analysis["expensive_operations"]:
                console.print("\n[bold red]⚠️ Expensive Operations:[/bold red]")
                for op in analysis["expensive_operations"]:
                    console.print(f"  • Line {op['line']}: {op['warning']}")
                    console.print(f"    Suggestion: {op['suggestion']}")
        
        elif output_format == "json":
            console.print_json(json.dumps(analysis, indent=2))
        
        console.print(f"\n[green]✅ Analysis completed![/green]")
        console.print(f"Total estimated gas: [cyan]{analysis['total_estimated_gas']:,}[/cyan]")
        
    except Exception as e:
        console.print(f"[red]❌ Analysis failed: {str(e)}[/red]")
        raise typer.Exit(1)


@app.command()
def template(
    template_name: str = typer.Argument(..., help="Template name (token, dex, oracle, dao)"),
    project_name: str = typer.Argument(..., help="Project name"),
    output_dir: str = typer.Option(".", "--output", "-o", help="Output directory")
):
    """
    Generate smart contract from templates.
    
    Available templates:
    - token: ERC-20 style token contract
    - dex: Automated Market Maker DEX
    - oracle: AI-powered oracle contract
    - dao: Governance DAO contract
    """
    console.print(f"[bold blue]📋 Generating {template_name} template: {project_name}[/bold blue]")
    
    templates = {
        "token": "strk.py",
        "dex": "templates/defi_dex.py", 
        "oracle": "templates/ai_oracle.py",
        "dao": "templates/dao_governance.py"
    }
    
    if template_name not in templates:
        console.print(f"[red]❌ Unknown template: {template_name}[/red]")
        console.print(f"[yellow]Available templates: {', '.join(templates.keys())}[/yellow]")
        raise typer.Exit(1)
    
    try:
        # Copy template file
        template_path = Path(templates[template_name])
        output_path = Path(output_dir) / f"{project_name}.py"
        
        if template_path.exists():
            content = template_path.read_text()
            # Replace template placeholders
            content = content.replace("TEMPLATE_NAME", project_name)
            output_path.write_text(content)
            
            console.print(f"[green]✅ Template generated: {output_path}[/green]")
            console.print(f"[dim]Next steps:[/dim]")
            console.print(f"[dim]  1. py0g compile {output_path}[/dim]")
            console.print(f"[dim]  2. py0g deploy {output_path}[/dim]")
        else:
            console.print(f"[red]❌ Template file not found: {template_path}[/red]")
            raise typer.Exit(1)
    
    except Exception as e:
        console.print(f"[red]❌ Template generation failed: {str(e)}[/red]")
        raise typer.Exit(1)


@app.command()
def version():
    """Show py0g version information."""
    console.print(Panel.fit("[PY0G] py0g v0.2.0", title="Python-first Smart Contract CLI"))
    console.print("Python-first smart contract toolkit for 0G Galileo blockchain")
    console.print("Bridging Web2 developers to Web3 using only Python! [PYTHON]")


if __name__ == "__main__":
    app()