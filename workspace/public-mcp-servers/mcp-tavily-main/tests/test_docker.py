import os
import shutil
import subprocess
import pytest

# Determine the project root directory (one level up from tests)
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))

@pytest.fixture(scope="session")
def docker_cli():
    """Ensure Docker CLI is available, otherwise skip tests."""
    docker = shutil.which("docker")
    if docker is None:
        pytest.skip("Docker CLI is not available")
    return docker

def test_dockerfile_exists():
    """Check that the Dockerfile exists in the project root."""
    dockerfile = os.path.join(PROJECT_ROOT, "Dockerfile")
    assert os.path.isfile(dockerfile), "Dockerfile is missing"

def test_docker_build_and_help(docker_cli):
    """Build the Docker image and verify the help message."""
    image = "mcp_tavily_test_image"
    # Build the Docker image
    build_cmd = [docker_cli, "build", "-t", image, "."]
    result = subprocess.run(
        build_cmd,
        cwd=PROJECT_ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    assert result.returncode == 0, f"Docker build failed: {result.stdout}"

    # Run the container with the help flag
    run_cmd = [docker_cli, "run", "--rm", image, "-h"]
    result = subprocess.run(
        run_cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    assert result.returncode == 0, f"Docker run -h failed: {result.stdout}"
    # Verify expected help text from the module's argparse description
    assert (
        "give a model the ability to perform AI-powered web searches using Tavily"
        in result.stdout
    ), "Help message content is incorrect"

    # Clean up the Docker image
    subprocess.run([docker_cli, "rmi", image], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)