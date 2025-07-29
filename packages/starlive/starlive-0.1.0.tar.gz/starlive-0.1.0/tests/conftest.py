import subprocess
import time

import pytest


@pytest.fixture(scope="session")
def app_server():
    """Start the StarLive app server for E2E tests."""
    # Start the server in a subprocess
    server_process = subprocess.Popen(
        ["python", "examples/basic_app.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    # Wait for server to start up
    time.sleep(3)

    # Check if server is running
    if server_process.poll() is not None:
        stdout, stderr = server_process.communicate()
        pytest.fail(f"Server failed to start: {stderr.decode()}")

    yield "http://127.0.0.1:8001"

    # Clean up
    server_process.terminate()
    server_process.wait(timeout=5)
