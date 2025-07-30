import os
import tempfile
from pathlib import Path

import pytest
import yaml

from dtu_compute.run_config import GPU, ConfigProcessor, JobConfig, Notification, Walltime
from dtu_compute.utils import adjectives, nouns


@pytest.fixture
def temp_config_file():
    """Create a temporary configuration file for testing."""
    with tempfile.NamedTemporaryFile(suffix=".yaml", delete=False) as tmp:
        yield Path(tmp.name)
    os.unlink(tmp.name)


class TestConfigProcessor:
    """Test cases for the ConfigProcessor class."""

    def test_basic_config_processing(self, temp_config_file):
        """Test basic configuration processing without substitutions."""
        config = {
            "jobname": "test_job",
            "queue": "gpuv100",
            "walltime": {"hours": 1, "minutes": 30},
            "memory": 16,
            "gpu": {"num_gpus": 1, "select": "V100"},
            "commands": ["python train.py", "python evaluate.py"],
        }

        with open(temp_config_file, "w") as f:
            yaml.dump(config, f)

        processor = ConfigProcessor(temp_config_file)
        processor.process()
        job_config = processor.get_job_config()

        assert isinstance(job_config, JobConfig)
        assert job_config.jobname == "test_job"
        assert job_config.queue == "gpuv100"
        assert job_config.walltime.hours == 1
        assert job_config.walltime.minutes == 30
        assert job_config.memory == 16
        assert job_config.gpu.num_gpus == 1
        assert job_config.gpu.select == "V100"
        assert job_config.commands == ["python train.py", "python evaluate.py"]

    def test_substitution_in_config(self, temp_config_file):
        """Test placeholder substitution in configuration."""
        config = {
            "substitutions": {"job_prefix": "experiment", "gpu_count": 2, "script_path": "/path/to/scripts"},
            "jobname": "${job_prefix}_test",
            "queue": "gpuv100",
            "walltime": {"hours": 2, "minutes": 0},
            "memory": 32,
            "gpu": {"num_gpus": "${gpu_count}", "select": "A100"},
            "commands": ["python ${script_path}/train.py", "python ${script_path}/evaluate.py"],
        }

        with open(temp_config_file, "w") as f:
            yaml.dump(config, f)

        processor = ConfigProcessor(temp_config_file)
        processor.process()
        job_config = processor.get_job_config()

        assert job_config.jobname == "experiment_test"
        assert job_config.gpu.num_gpus == 2  # converted from string to int by pydantic
        assert job_config.commands[0] == "python /path/to/scripts/train.py"
        assert job_config.commands[1] == "python /path/to/scripts/evaluate.py"


class TestJobConfig:
    """Test cases for the JobConfig class."""

    def test_job_config_initialization(self):
        """Test JobConfig initialization with different parameters."""
        job_config = JobConfig(
            jobname="test_job",
            queue="cpu",
            walltime=Walltime(hours=2, minutes=30),
            memory=8,
            gpu=GPU(num_gpus=0),
            commands=["echo 'Hello World'"],
        )

        assert job_config.jobname == "test_job"
        assert job_config.std_out == "test_job.out"
        assert job_config.std_err == "test_job.err"

    def test_custom_output_files(self):
        """Test JobConfig with custom output file paths."""
        job_config = JobConfig(
            jobname="custom_out",
            walltime=Walltime(hours=1, minutes=0),
            std_out="custom.out",
            std_err="custom.err",
            gpu=GPU(num_gpus=0),
            commands=["python script.py"],
        )

        assert job_config.std_out == "custom.out"
        assert job_config.std_err == "custom.err"

    def test_random_job_name_generated(self):
        """Test that a random job name is generated when no jobname is provided."""
        job_config = JobConfig(
            queue="cpu",
            walltime=Walltime(hours=1, minutes=0),
            gpu=GPU(num_gpus=0),
            commands=["python script.py"],
        )
        jobname = job_config.jobname
        adj, noun, num = jobname.split("_")
        assert adj in adjectives
        assert noun in nouns
        assert num.isdigit()
        assert len(num) > 0

    def test_cores_adjusted_for_gpu(self):
        """Test that cores are adjusted to at least 4 per GPU."""
        # 1 GPU should ensure at least 4 cores
        job_config = JobConfig(
            cores=1,
            gpu=GPU(num_gpus=1),
            commands=["python script.py"],
        )
        assert job_config.cores == 4

        # 2 GPUs should ensure at least 8 cores
        job_config = JobConfig(
            cores=1,
            gpu=GPU(num_gpus=2),
            commands=["python script.py"],
        )
        assert job_config.cores == 8

        # Higher core count should be preserved
        job_config = JobConfig(
            cores=10,
            gpu=GPU(num_gpus=1),
            commands=["python script.py"],
        )
        assert job_config.cores == 10


class TestNotification:
    """Test cases for the Notification class."""

    def test_email_validation(self):
        """Test that an error is raised when an invalid email format is provided."""
        # Valid email should work
        valid_notification = Notification(email="user@example.com")
        assert valid_notification.email == "user@example.com"

        # Invalid emails should raise validation errors
        with pytest.raises(ValueError):
            Notification(email="invalid-email")

        with pytest.raises(ValueError):
            Notification(email="user@")

        with pytest.raises(ValueError):
            Notification(email="@example.com")

        with pytest.raises(ValueError):
            Notification(email="user@example")

    def test_notification_defaults(self):
        """Test that notification defaults are set correctly."""
        notification = Notification()
        assert notification.email == ""
        assert notification.email_on_start is False
        assert notification.email_on_end is False

    def test_notification_with_options(self):
        """Test notification with all options set."""
        notification = Notification(email="user@example.com", email_on_start=True, email_on_end=True)
        assert notification.email == "user@example.com"
        assert notification.email_on_start is True
        assert notification.email_on_end is True


class TestWalltime:
    """Test cases for the Walltime class."""

    def test_valid_walltime(self):
        """Test that valid walltime values are accepted."""
        # All zeros
        walltime = Walltime(hours=0, minutes=0)
        assert walltime.hours == 0
        assert walltime.minutes == 0

        # Maximum values
        walltime = Walltime(hours=23, minutes=59)
        assert walltime.hours == 23
        assert walltime.minutes == 59

        # Only hours
        walltime = Walltime(hours=5)
        assert walltime.hours == 5
        assert walltime.minutes == 15  # Default is 15 minutes

        # Only minutes
        walltime = Walltime(minutes=30)
        assert walltime.hours == 0
        assert walltime.minutes == 30

    def test_invalid_hours(self):
        """Test that invalid hour values raise validation errors."""
        # Negative hours
        with pytest.raises(ValueError):
            Walltime(hours=-1)

        # Hours > 23
        with pytest.raises(ValueError):
            Walltime(hours=24)

        with pytest.raises(ValueError):
            Walltime(hours=100)

    def test_invalid_minutes(self):
        """Test that invalid minute values raise validation errors."""
        # Negative minutes
        with pytest.raises(ValueError):
            Walltime(minutes=-1)

        # Minutes > 59
        with pytest.raises(ValueError):
            Walltime(minutes=60)

        with pytest.raises(ValueError):
            Walltime(minutes=100)


class TestGPU:
    """Test cases for the GPU class."""

    def test_gpu_initialization(self):
        """Test GPU initialization with different parameters."""
        gpu = GPU(num_gpus=2, memory=16, select="A100")
        assert gpu.num_gpus == 2
        assert gpu.memory == 16
        assert gpu.select == "A100"

    def test_gpu_defaults(self):
        """Test that GPU defaults are set correctly."""
        gpu = GPU(num_gpus=1)
        assert gpu.num_gpus == 1
        assert gpu.memory is None
        assert gpu.select is None

    def test_invalid_gpu_count(self):
        """Test that invalid GPU count raises validation errors."""
        with pytest.raises(ValueError):
            GPU(num_gpus=-1)

    def test_invalid_memory(self):
        """Test that invalid memory values raise validation errors."""
        with pytest.raises(ValueError):
            GPU(num_gpus=1, memory=-1)
