from pydantic import BaseModel


class HPCQueueStat(BaseModel):
    """Base class for HPC queue statistics."""

    queue_name: str
    pending_jobs: int | None = None  # Number of pending jobs in the queue, will set at runtime


class CPUQueueStat(HPCQueueStat):
    """Queue stat for CPU resources in HPC."""

    num_cores: int


class GPUQueueStat(HPCQueueStat):
    """Queue stat for GPU resources in HPC."""

    num_nodes: int
    num_gpus: int  # Number of GPUs per node
    gpu_vram: int


HPC_REGISTRY: dict[str, HPCQueueStat] = {}


def register_queue_stat(queue_stat: HPCQueueStat) -> None:
    """Register a queue stat in the global registry."""
    if queue_stat.queue_name in HPC_REGISTRY:
        raise ValueError(f"Queue stat for {queue_stat.queue_name} already registered.")
    HPC_REGISTRY[queue_stat.queue_name] = queue_stat


register_queue_stat(CPUQueueStat(queue_name="hpc", num_cores=3980))
register_queue_stat(CPUQueueStat(queue_name="compute", num_cores=1260))
register_queue_stat(GPUQueueStat(queue_name="gpua100_gpu40gb", num_nodes=4, num_gpus=2, gpu_vram=40))
register_queue_stat(GPUQueueStat(queue_name="gpua100_gpu80gb", num_nodes=6, num_gpus=2, gpu_vram=80))
register_queue_stat(GPUQueueStat(queue_name="gpuv100_gpu16gb", num_nodes=6, num_gpus=2, gpu_vram=16))
register_queue_stat(GPUQueueStat(queue_name="gpuv100_gpu32gb", num_nodes=8, num_gpus=2, gpu_vram=32))
register_queue_stat(GPUQueueStat(queue_name="gpuv100_gpu32gb_nvlink", num_nodes=3, num_gpus=4, gpu_vram=32))
register_queue_stat(GPUQueueStat(queue_name="gpua10", num_nodes=1, num_gpus=2, gpu_vram=24))
register_queue_stat(GPUQueueStat(queue_name="gpua40", num_nodes=1, num_gpus=2, gpu_vram=48))
register_queue_stat(GPUQueueStat(queue_name="gpuh100", num_nodes=2, num_gpus=2, gpu_vram=80))
register_queue_stat(GPUQueueStat(queue_name="p1", num_nodes=7, num_gpus=2, gpu_vram=80))
