import subprocess
import time

import pytest
import requests


def pytest_addoption(parser):
    """Add command line option to choose which framework to test."""
    parser.addoption(
        "--framework",
        action="store",
        default="starlette",
        choices=["starlette", "fastapi", "both"],
        help="Choose which framework to test: starlette, fastapi, or both",
    )


@pytest.fixture(scope="session")
def framework_choice(request):
    """Get the framework choice from command line."""
    return request.config.getoption("--framework")


@pytest.fixture(scope="session", params=["starlette", "fastapi"])
def framework(request, framework_choice):
    """Parametrized fixture for framework testing."""
    # Skip frameworks that weren't selected
    if framework_choice == "both":
        # Test both frameworks
        return request.param
    elif framework_choice != request.param:
        pytest.skip(f"Skipping {request.param}, testing only {framework_choice}")
    return request.param


@pytest.fixture(scope="session")
def app_config(framework):
    """Get configuration for the selected framework."""
    configs = {
        "starlette": {
            "module": "examples.starlette_app",
            "port": 8001,
            "url": "http://127.0.0.1:8001",
        },
        "fastapi": {
            "module": "examples.fastapi_app",
            "port": 8002,
            "url": "http://127.0.0.1:8002",
        },
    }
    return configs[framework]


def wait_for_server(url, timeout=30):
    """Wait for server to be ready."""
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                return True
        except (
            requests.exceptions.RequestException,
            requests.exceptions.ConnectionError,
        ):
            pass
        time.sleep(1)
    return False


@pytest.fixture(scope="session")
def app_server(app_config):
    """Start the app server for E2E tests."""
    # Start the server in a subprocess using uv run to ensure correct environment
    server_process = subprocess.Popen(
        ["uv", "run", "python", "-m", app_config["module"]],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env={**subprocess.os.environ, "PYTEST_CURRENT_TEST": "true"},
    )

    # Wait for server to start up and be responsive
    if not wait_for_server(app_config["url"]):
        # Server didn't start properly, get the output
        try:
            stdout, stderr = server_process.communicate(timeout=5)
            pytest.fail(
                f"Server failed to start properly. STDOUT: {stdout.decode()}, STDERR: {stderr.decode()}"
            )
        except subprocess.TimeoutExpired:
            server_process.kill()
            stdout, stderr = server_process.communicate()
            pytest.fail(
                f"Server timed out. STDOUT: {stdout.decode()}, STDERR: {stderr.decode()}"
            )

    yield app_config["url"]

    # Clean up
    server_process.terminate()
    try:
        server_process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        server_process.kill()
        server_process.wait()
