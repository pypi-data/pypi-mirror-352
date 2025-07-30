import os
import re
from pathlib import Path

import pytest
from typer.testing import CliRunner

from dtu_compute.config import ConfigManager
from dtu_compute.hpc.cli import app

runner = CliRunner()


@pytest.fixture
def config_dir():
    """Fixture to create a temporary configuration directory."""
    return Path(__file__).parent / "configs"


@pytest.fixture
def config_file():
    """Fixture to path to the DTU configuration file."""
    cwd = os.getcwd()
    return Path(cwd) / "dtu.toml"


def test_hpc_cli_run(config_file):
    """Test the help command of the HPC CLI."""
    result = runner.invoke(app, ["run", "whoami", "--config-file", str(config_file)])
    assert result.exit_code == 0
    config_manager = ConfigManager(config_file)
    config = config_manager.load_config()
    assert config.auth.dtu_username == result.output.strip("\n")


@pytest.mark.parametrize(
    ("run_config", "expected_queue"),
    [
        ("example1.yaml", "compute"),
        ("example2.yaml", "compute"),
    ],
)
def test_hpc_cli_submit(run_config, expected_queue, config_dir, config_file):
    """Test the submit command of the HPC CLI."""
    run_config_path = config_dir / run_config
    result = runner.invoke(app, ["submit", str(run_config_path), "--config-file", str(config_file)])
    assert result.exit_code == 0

    # Match "Job <some_number> is submitted to queue <expected_queue>."
    pattern = rf"Job <\d+> is submitted to queue <{re.escape(expected_queue)}>\."
    assert re.search(pattern, result.output), f"Expected queue line not found in output: {result.output}"
