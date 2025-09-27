"""
0G Compute Integration for py0g

Enables off-chain computation for smart contracts:
- Heavy computational tasks
- AI model inference
- Data processing pipelines
- Batch operations
"""

import json
import asyncio
from typing import Dict, Any, Optional, List, Callable
from dataclasses import dataclass
from enum import Enum


class ComputeTaskType(Enum):
    """Types of compute tasks."""
    AI_INFERENCE = "ai_inference"
    DATA_PROCESSING = "data_processing"
    BATCH_OPERATION = "batch_operation"
    OPTIMIZATION = "optimization"
    SIMULATION = "simulation"


@dataclass
class ComputeTask:
    """Compute task definition."""
    task_id: str
    task_type: ComputeTaskType
    input_data: Dict[str, Any]
    compute_requirements: Dict[str, Any]
    callback_contract: Optional[str] = None
    max_execution_time: int = 300  # seconds


@dataclass
class ComputeResult:
    """Result of compute operation."""
    task_id: str
    success: bool
    result_data: Dict[str, Any]
    execution_time: float
    compute_cost: float
    error_message: Optional[str] = None


class ZeroGComputeClient:
    """Client for 0G Compute Network."""
    
    def __init__(self, compute_endpoint: str = "https://compute-testnet.0g.ai"):
        """Initialize 0G Compute client."""
        self.endpoint = compute_endpoint
        self.active_tasks: Dict[str, ComputeTask] = {}
    
    async def submit_ai_inference_task(
        self, 
        model_name: str, 
        input_data: Dict[str, Any],
        callback_contract: Optional[str] = None
    ) -> str:
        """Submit AI inference task to 0G Compute."""
        task_id = f"ai_{hash(str(input_data))}"
        
        task = ComputeTask(
            task_id=task_id,
            task_type=ComputeTaskType.AI_INFERENCE,
            input_data={
                "model_name": model_name,
                "input": input_data
            },
            compute_requirements={
                "gpu_required": True,
                "memory_gb": 8,
                "cpu_cores": 4
            },
            callback_contract=callback_contract
        )
        
        self.active_tasks[task_id] = task
        
        # Simulate task submission
        print(f"🤖 Submitted AI inference task: {task_id}")
        print(f"   Model: {model_name}")
        print(f"   Compute requirements: GPU + 8GB RAM")
        
        return task_id
    
    async def submit_batch_operation(
        self,
        operation_type: str,
        batch_data: List[Dict[str, Any]],
        callback_contract: Optional[str] = None
    ) -> str:
        """Submit batch operation to 0G Compute."""
        task_id = f"batch_{hash(str(batch_data))}"
        
        task = ComputeTask(
            task_id=task_id,
            task_type=ComputeTaskType.BATCH_OPERATION,
            input_data={
                "operation": operation_type,
                "batch_size": len(batch_data),
                "data": batch_data
            },
            compute_requirements={
                "cpu_cores": 8,
                "memory_gb": 16,
                "parallel_workers": 4
            },
            callback_contract=callback_contract
        )
        
        self.active_tasks[task_id] = task
        
        print(f"⚡ Submitted batch operation: {task_id}")
        print(f"   Operation: {operation_type}")
        print(f"   Batch size: {len(batch_data)}")
        
        return task_id
    
    async def get_task_result(self, task_id: str) -> Optional[ComputeResult]:
        """Get result of compute task."""
        if task_id not in self.active_tasks:
            return None
        
        task = self.active_tasks[task_id]
        
        # Simulate compute result
        if task.task_type == ComputeTaskType.AI_INFERENCE:
            result_data = {
                "prediction": [0.85, 0.12, 0.03],
                "confidence": 0.85,
                "model_version": "v1.2.3"
            }
        elif task.task_type == ComputeTaskType.BATCH_OPERATION:
            result_data = {
                "processed_items": len(task.input_data.get("data", [])),
                "success_rate": 0.98,
                "failed_items": []
            }
        else:
            result_data = {"status": "completed"}
        
        return ComputeResult(
            task_id=task_id,
            success=True,
            result_data=result_data,
            execution_time=2.5,
            compute_cost=0.001,  # A0GI
            error_message=None
        )
    
    def list_active_tasks(self) -> List[str]:
        """List active compute tasks."""
        return list(self.active_tasks.keys())


class AIModelContract:
    """Smart contract template for AI model integration."""
    
    def __init__(self, owner: str, model_name: str):
        """Initialize AI model contract."""
        self.owner = owner
        self.model_name = model_name
        self.inference_count = 0
        self.compute_client = ZeroGComputeClient()
    
    async def run_inference(self, caller: str, input_data: Dict[str, Any]) -> str:
        """Run AI inference using 0G Compute."""
        if caller != self.owner:
            return "Unauthorized"
        
        # Submit to 0G Compute
        task_id = await self.compute_client.submit_ai_inference_task(
            model_name=self.model_name,
            input_data=input_data,
            callback_contract=self.owner  # Contract address
        )
        
        self.inference_count += 1
        return task_id
    
    async def get_inference_result(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get inference result."""
        result = await self.compute_client.get_task_result(task_id)
        if result and result.success:
            return result.result_data
        return None


# CLI integration
def add_compute_commands():
    """Add compute commands to py0g CLI."""
    compute_commands = {
        "compute run": "Run computation on 0G Compute network",
        "compute status": "Check status of compute tasks",
        "compute result": "Get result of compute task",
        "compute models": "List available AI models"
    }
    return compute_commands
