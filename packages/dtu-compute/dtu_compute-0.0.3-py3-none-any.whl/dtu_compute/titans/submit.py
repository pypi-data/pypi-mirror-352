from pathlib import Path

from dtu_compute.config import Config
from dtu_compute.connection import ClusterConnection
from dtu_compute.run_config import JobConfig
from dtu_compute.titans.registry import TITAN_REGISTRY, TitanQueueStat


class SlurmJob:
    """Class to generate a Slurm job script from a job configuration."""

    def __init__(self, config: Config, jobconfig: JobConfig, target_dir: str | None = None) -> None:
        self.config = config
        self.jobconfig = jobconfig
        self.target_dir = target_dir

    def submit(self, connection: ClusterConnection) -> None:
        """Submit the job script to the cluster using the provided connection."""
        submit_file = self.process(connection)
        connection.put(submit_file, remote_path=self.target_dir)
        connection.run(f"cd {self.target_dir} && sbatch {submit_file.name}")
        connection.run(f"rm {self.target_dir}/{submit_file.name}")

    def process(self, connection: ClusterConnection) -> Path:
        """Process the job configuration and create a Slurm script file."""
        self.determine_queue(connection=connection)

        # Create the script file
        script_content = self.to_script()

        # Create unique file name
        save_folder = Path(".dtu_compute")
        save_folder.mkdir(parents=True, exist_ok=True)
        base_name = self.jobconfig.jobname.replace(" ", "_").replace("/", "_")
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
        self.get_cluster_stats(TITAN_REGISTRY, connection)

        if self.jobconfig.gpu is None or self.jobconfig.gpu.num_gpus == 0:
            # If no GPUs are requested, set the queue to the CPU nodes
            self.jobconfig.queue = "comp-cpu01,comp-cpu02"

        elif self.jobconfig.gpu is not None:
            # If GPUs are requested, find the queues that can accommodate the job
            queues = []
            for queue_stat in TITAN_REGISTRY.values():
                if (
                    queue_stat.num_gpus >= self.jobconfig.gpu.num_gpus
                    and queue_stat.gpu_vram >= self.jobconfig.gpu.memory
                ):
                    queues.append(queue_stat.queue_name)

            self.jobconfig.queue = ",".join(queues) if queues else None

    def get_cluster_stats(self, registry: dict[str, TitanQueueStat], connection: ClusterConnection):
        """Get the cluster statistics and update the registry with queue stats."""
        result = connection.run('squeue -h -o "%N" | sort | uniq -c', hide=True)
        if result.exited != 0:
            return  # If squeue command fails, we cannot determine the queue stats
        lines = result.stdout.strip().split("\n")

        usage = {}
        for line in lines:
            count, node = line.strip().split(maxsplit=1)
            usage[node] = count

        for queue_name in registry:
            registry[queue_name].pending_jobs = int(usage[queue_name]) if queue_name in usage else 0

    def to_script(self) -> str:
        """Convert the job configuration to a Slurm script."""
        cfg = self.jobconfig
        lines = [
            "#!/bin/bash",
            "# Slurm job script",
            f"#SBATCH --job-name={cfg.jobname}",
            f"#SBATCH --cpus-per-task={cfg.cores}",
            f"#SBATCH --mem={cfg.memory}gb",
            f"#SBATCH --time={cfg.walltime.hours:02}:{cfg.walltime.minutes:02}",
            f"#SBATCH --output={cfg.std_out}",
            f"#SBATCH --error={cfg.std_err}",
            "#SBATCH --export=ALL",  # Export all environment variables
        ]
        if cfg.notification:
            events = []
            if cfg.notification.email_on_start:
                events.append("BEGIN")
            if cfg.notification.email_on_end:
                events.append("END, FAIL")
            lines += [
                f"#SBATCH --mail-user={cfg.notification.email}",
                f"#SBATCH --mail-type={','.join(events)}",
            ]

        if cfg.queue:
            lines.append(f"#SBATCH --nodelist={cfg.queue}")

        if cfg.gpu.num_gpus > 0:
            lines.append("#SBATCH --partition=titans")
            if cfg.gpu.select:
                lines += [f"#SBATCH --gres=gpu:{cfg.gpu.select}:{cfg.gpu.num_gpus}"]
            else:
                lines += [f"#SBATCH --gres=gpu:{cfg.gpu.num_gpus}"]
        else:
            lines.append("#SBATCH --partition=cyclops")

        lines.append("# Commands")
        lines += ["", *cfg.commands]
        lines.append('echo "Done: $(date +%F-%R:%S)"')
        return "\n".join([line for line in lines if line])
