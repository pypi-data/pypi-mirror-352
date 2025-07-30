from pydantic import BaseModel


class TitanQueueStat(BaseModel):
    """Base class for Titan queue statistics."""

    queue_name: str
    pending_jobs: int | None = None  # Number of pending jobs in the queue, will
    num_gpus: int
    gpu_vram: int


TITAN_REGISTRY: dict[str, TitanQueueStat] = {}


def register_titan_queue_stat(queue_stat: TitanQueueStat) -> None:
    """Register a Titan queue stat in the global registry."""
    if queue_stat.queue_name in TITAN_REGISTRY:
        raise ValueError(f"Queue stat for {queue_stat.queue_name} already registered.")
    TITAN_REGISTRY[queue_stat.queue_name] = queue_stat


register_titan_queue_stat(TitanQueueStat(queue_name="comp-gpu01", num_gpus=8, gpu_vram=16))
register_titan_queue_stat(TitanQueueStat(queue_name="comp-gpu02", num_gpus=8, gpu_vram=11))
register_titan_queue_stat(TitanQueueStat(queue_name="comp-gpu03", num_gpus=8, gpu_vram=11))
register_titan_queue_stat(TitanQueueStat(queue_name="comp-gpu04", num_gpus=8, gpu_vram=24))
register_titan_queue_stat(TitanQueueStat(queue_name="comp-gpu05", num_gpus=8, gpu_vram=24))
register_titan_queue_stat(TitanQueueStat(queue_name="comp-gpu06", num_gpus=8, gpu_vram=11))
register_titan_queue_stat(TitanQueueStat(queue_name="comp-gpu07", num_gpus=8, gpu_vram=16))
register_titan_queue_stat(TitanQueueStat(queue_name="comp-gpu08", num_gpus=4, gpu_vram=16))
register_titan_queue_stat(TitanQueueStat(queue_name="comp-gpu09", num_gpus=8, gpu_vram=11))
register_titan_queue_stat(TitanQueueStat(queue_name="comp-gpu10", num_gpus=7, gpu_vram=12))
register_titan_queue_stat(TitanQueueStat(queue_name="comp-gpu11", num_gpus=8, gpu_vram=16))
register_titan_queue_stat(TitanQueueStat(queue_name="comp-gpu12", num_gpus=7, gpu_vram=12))
register_titan_queue_stat(TitanQueueStat(queue_name="comp-gpu13", num_gpus=4, gpu_vram=48))
register_titan_queue_stat(TitanQueueStat(queue_name="comp-gpu14", num_gpus=8, gpu_vram=24))
register_titan_queue_stat(TitanQueueStat(queue_name="comp-cpu01", num_gpus=0, gpu_vram=0))
register_titan_queue_stat(TitanQueueStat(queue_name="comp-cpu02", num_gpus=0, gpu_vram=0))
