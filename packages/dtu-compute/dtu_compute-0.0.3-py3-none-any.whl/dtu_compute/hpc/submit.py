from pathlib import Path

from dtu_compute.config import Config
from dtu_compute.connection import ClusterConnection
from dtu_compute.hpc.registry import HPC_REGISTRY, GPUQueueStat, HPCQueueStat
from dtu_compute.run_config import JobConfig


class LSFJob:
    """Class to generate a LSF job script from a job configuration."""

    def __init__(self, config: Config, jobconfig: JobConfig, target_dir: str | None = None) -> None:
        self.config = config
        self.jobconfig = jobconfig
        self.target_dir = target_dir

    def submit(self, connection: ClusterConnection) -> None:
        """Submit the job script to the cluster using the provided connection."""
        submit_file = self.process(connection)
        connection.put(submit_file, remote_path=self.target_dir)
        connection.run(f"cd {self.target_dir} && bsub < {submit_file.name}")
        connection.run(f"rm {self.target_dir}/{submit_file.name}")

    def process(self, connection: ClusterConnection) -> Path:
        """Process the job configuration and create a LSF script file."""
        self.determine_queue(connection=connection)

        # Create the script file
        script_content = self.to_script()

        # Create unique file name
        save_folder = Path(".dtu_compute")
        save_folder.mkdir(parents=True, exist_ok=True)
        base_name = self.jobconfig.jobname.replace(" ", "_").replace("-", "_")
        extension = ".sh"
        version = 1
        save_path = save_folder / f"{base_name}{extension}"
        while save_path.exists():
            save_path = save_folder / f"{base_name}_{version}{extension}"
            version += 1

        # Write the script content to the file
        with save_path.open("w") as f:
            f.write(script_content)
        return save_path

    def determine_queue(self, connection: ClusterConnection):
        """Determine the appropriate queue for the job if the user did not specify one."""
        if self.jobconfig.queue:
            return

        # To determine the queue, we need to get the cluster stats
        self.get_cluster_stats(HPC_REGISTRY, connection)

        # Filter out ignored queues
        self.filter_queues(HPC_REGISTRY)

        if self.jobconfig.gpu is None or self.jobconfig.gpu.num_gpus == 0:
            # If no GPUs are requested, choose between CPU queues based on load and available cores
            hpc_stat = HPC_REGISTRY.get("hpc")
            compute_stat = HPC_REGISTRY.get("compute")

            # Calculate load per core (pending jobs / available cores)
            hpc_load = (
                hpc_stat.pending_jobs / hpc_stat.num_cores  # ty:ignore
                if hpc_stat.pending_jobs is not None
                else float("inf")
            )
            compute_load = (
                compute_stat.pending_jobs / compute_stat.num_cores  # ty:ignore
                if compute_stat.pending_jobs is not None
                else float("inf")
            )

            # Choose the queue with the lower load per core
            if hpc_load <= compute_load:
                self.jobconfig.queue = "hpc"
            else:
                self.jobconfig.queue = "compute"

        elif self.jobconfig.gpu is not None:
            best_queue = None
            best_score = float("inf")  # Lower scores are better

            for queue_stat in HPC_REGISTRY.values():
                if not isinstance(queue_stat, GPUQueueStat):
                    continue

                # Check if the queue satisfies both GPU count and VRAM requirements
                if (
                    queue_stat.num_gpus >= self.jobconfig.gpu.num_gpus
                    and queue_stat.gpu_vram >= self.jobconfig.gpu.memory
                ):
                    score = (
                        queue_stat.pending_jobs / queue_stat.num_gpus  # ty:ignore
                        if queue_stat.pending_jobs is not None
                        else float("inf")
                    )
                    if score < best_score:
                        best_score = score
                        best_queue = queue_stat

            # If we found a suitable queue, use a default one
            if best_queue is None:
                self.jobconfig.queue = "gpua100"
            else:
                if "_" in best_queue.queue_name:
                    queue_name, gpu_select = best_queue.queue_name.split("_")[:2]
                    self.jobconfig.queue = queue_name
                    self.jobconfig.gpu.select = gpu_select
                else:
                    self.jobconfig.queue = best_queue.queue_name

    def get_cluster_stats(self, registry: dict[str, HPCQueueStat], connection: ClusterConnection) -> None:
        """Get the cluster statistics and update the registry with queue stats."""
        result = connection.run("bqueues", hide=True)
        if result.exited != 0:
            return  # If bqueues command fails, we cannot determine the queue stats
        lines = result.stdout.strip().splitlines()

        header = lines[0].split()
        try:
            queue_idx = header.index("QUEUE_NAME")
            pend_idx = header.index("PEND")
        except ValueError:
            raise RuntimeError("Unexpected bqueues output format")

        usage = {}
        for line in lines[1:]:
            fields = line.split()
            if len(fields) <= max(queue_idx, pend_idx):
                continue
            queue = fields[queue_idx]
            pending = int(fields[pend_idx])
            usage[queue] = pending

        for queue_name in registry:
            qn = queue_name.split("_")[0]  # Get the base queue name
            if qn in usage:
                registry[queue_name].pending_jobs = usage[qn]

    def filter_queues(self, registry: dict[str, HPCQueueStat]) -> None:
        """Filter the queues in the registry based on the ignore_queues list."""
        ignore_queues = self.config.hpc.ignore_queues
        for queue_name in list(registry.keys()):
            if queue_name in ignore_queues:
                del registry[queue_name]

    def to_script(self) -> str:
        """Convert the job configuration to a LSF script."""
        cfg = self.jobconfig
        lines = [
            "#!/bin/sh",
            "# LSF Job options",
            f"#BSUB -J {cfg.jobname}",
            f"#BSUB -q {cfg.queue}",
            f"#BSUB -n {cfg.cores}",
            '#BSUB -R "span[hosts=1]"',  # all cores on the same host
            f"#BSUB -R 'rusage[mem={cfg.memory}GB]'",
            f"#BSUB -o {cfg.std_out}",
            f"#BSUB -e {cfg.std_err}",
        ]

        if cfg.walltime:
            lines.append(f"#BSUB -W {cfg.walltime.hours:02}:{cfg.walltime.minutes:02}")

        if cfg.notification:
            if cfg.notification.email:
                lines.append(f"#BSUB -u {cfg.notification.email}")
            if cfg.notification.email_on_start:
                lines.append("#BSUB -B")
            if cfg.notification.email_on_end:
                lines.append("#BSUB -N")

        if cfg.gpu:
            lines.append(f'#BSUB -gpu "num={cfg.gpu.num_gpus}:mode=exclusive_process"')
            if cfg.gpu.select:
                lines.append(f'#BSUB -R "select[{cfg.gpu.select}]"')

        lines.append("# Commands")
        lines += ["", *cfg.commands]
        lines.append('echo "Done: $(date +%F-%R:%S)"')
        return "\n".join([line for line in lines if line])
