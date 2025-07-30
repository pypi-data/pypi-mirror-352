import re
from abc import ABC
from pathlib import Path

import yaml
from loguru import logger
from pydantic import BaseModel, ConfigDict, Field

from dtu_compute.utils import generate_name


class Walltime(BaseModel):
    """Configuration for job walltime."""

    model_config = ConfigDict(extra="forbid")

    hours: int = Field(0, ge=0, le=23)
    minutes: int = Field(15, ge=0, le=59)


class Notification(BaseModel):
    """Configuration for job notifications."""

    model_config = ConfigDict(extra="forbid")

    email: str = Field("", pattern=r"^[\w\.-]+@[\w\.-]+\.\w+$", description="Email address for notifications")
    email_on_start: bool = False
    email_on_end: bool = False


class GPU(BaseModel):
    """Configuration for GPU resources."""

    model_config = ConfigDict(extra="forbid")

    num_gpus: int = Field(1, ge=0, description="Number of GPUs required for the job")
    memory: int | None = Field(None, ge=0, description="Minimum GPU memory required in GB (None for no minimum)")
    select: str | None = Field(
        None,
        description="Type of GPU required (e.g., 'A100', 'V100', 'T4'). If None, no specific type is requested.",
    )


class JobConfig(BaseModel):
    """Configuration for a job to be submitted to a scheduler."""

    model_config = ConfigDict(extra="forbid")

    jobname: str | None = Field(None, description="Name of the job")
    cores: int = Field(4, ge=1, description="Number of CPU cores required for the job")
    queue: str | None = Field(None, description="Queue to submit the job to (None for default queue)")
    walltime: Walltime | None = Field(None, description="Walltime for the job (None for default 15 min)")
    std_out: str | None = Field(None, description="Path to the standard output file (None for default location)")
    std_err: str | None = Field(None, description="Path to the standard error output file (None for default location)")
    memory: int = Field(10, ge=1, description="Memory required for the job in GB")
    notification: Notification | None = Field(
        None, description="Notification settings for the job (None for no notifications)"
    )
    gpu: GPU | None = Field(
        None,
        description="GPU configuration for the job (None for no GPU requirements)",
    )
    commands: list[str]

    def model_post_init(self, context):
        """Post-initialization processing to replace hyphens with underscores in jobname."""
        # Set default value for jobname, std_out, and std_err if they are None
        if self.jobname is None:
            self.jobname = generate_name()
        if self.std_out is None:
            self.std_out = f"{self.jobname}.out"
        if self.std_err is None:
            self.std_err = f"{self.jobname}.err"

        # Default to 15min walltime if not specified
        if self.walltime is None:
            self.walltime = Walltime(hours=0, minutes=15)

        # Ensure at least 4 cores per GPU
        if self.gpu is not None and self.gpu.num_gpus > 0:
            if self.cores < 4 * self.gpu.num_gpus:
                logger.warning(
                    f"You requested {self.cores} cores, but at least {4 * self.gpu.num_gpus} cores are required for"
                    f" {self.gpu.num_gpus} GPUs. Setting cores to {4 * self.gpu.num_gpus}."
                )
            self.cores = max(self.cores, 4 * self.gpu.num_gpus)


class ConfigProcessor(ABC):
    """Abstract base class for processing configuration files."""

    config: dict
    processed_config: list[dict] | dict | None = None

    def __init__(self, config_path: Path):
        """Initialize the ConfigProcessor with either a path to a config file or a config dictionary.

        Args:
            config_path: Path to the YAML config file
            config_dict: Dictionary containing configuration (alternative to config_path)

        """
        with config_path.open("r") as f:
            self.config = yaml.safe_load(f)

    def _substitute_placeholders(self, config, substitutions):
        """Recursively traverse the config and replace placeholders in strings with values from substitutions."""
        if isinstance(config, dict):
            return {k: self._substitute_placeholders(v, substitutions) for k, v in config.items()}
        elif isinstance(config, list):
            return [self._substitute_placeholders(item, substitutions) for item in config]
        elif isinstance(config, str):
            # Replace all occurrences of ${key} with the corresponding substitution value
            def replacer(match):
                key = match.group(1)
                return str(substitutions.get(key, match.group(0)))

            return re.sub(r"\$\{([^}]+)\}", replacer, config)
        else:
            return config

    def process(self) -> None:
        """Process the config by substituting placeholders."""
        config_copy = self.config.copy()
        substitutions = config_copy.pop("substitutions", {})

        if substitutions:
            self.processed_config = self._substitute_placeholders(config_copy, substitutions)
        else:
            self.processed_config = config_copy

    def get_job_config(self):
        """Return a JobConfig object built from the processed configuration."""
        if self.processed_config is None:
            self.process()

        if isinstance(self.processed_config, list):
            return [JobConfig(**job) for job in self.processed_config]  # type: ignore
        return JobConfig(**self.processed_config)  # type: ignore
