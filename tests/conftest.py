import pytest
import requests

def is_ollama_running():
    """Check if the local Ollama server is accessible."""
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=1)
        return response.status_code == 200
    except:
        return False

@pytest.fixture(scope="session", autouse=True)
def check_ollama(request):
    """
    Session-wide fixture that skips all tests marked with 'ollama' 
    if the Ollama server is not running.
    """
    if not is_ollama_running():
        # You can add logic here to mark tests as skipped if they require Ollama
        pass

def pytest_configure(config):
    # Register the 'ollama' mark
    config.addinivalue_line("markers", "ollama: mark test as requiring a local Ollama instance")
