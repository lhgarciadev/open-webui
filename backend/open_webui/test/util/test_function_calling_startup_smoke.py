import os
import subprocess
import sys
from pathlib import Path

import pytest


def _backend_dir() -> Path:
    return Path(__file__).resolve().parents[3]


def _bootstrap_script() -> str:
    return """
import importlib.machinery
import os
import sys
import types

torch_stub = types.ModuleType("torch")
torch_stub.__spec__ = importlib.machinery.ModuleSpec("torch", loader=None)
torch_stub.backends = types.SimpleNamespace(
    mps=types.SimpleNamespace(is_available=lambda: False, is_built=lambda: False)
)
torch_stub.cuda = types.SimpleNamespace(is_available=lambda: False)
sys.modules["torch"] = torch_stub

from open_webui.config import DEFAULT_FUNCTION_CALLING_MODE

print(DEFAULT_FUNCTION_CALLING_MODE.value)
"""


@pytest.mark.parametrize("mode", ["native", "default"])
def test_backend_config_bootstrap_in_both_function_calling_modes(mode: str):
    env = os.environ.copy()
    env["PYTHONPATH"] = str(_backend_dir())
    env["DEFAULT_FUNCTION_CALLING_MODE"] = mode

    result = subprocess.run(
        [sys.executable, "-c", _bootstrap_script()],
        env=env,
        capture_output=True,
        text=True,
        timeout=60,
    )

    assert result.returncode == 0, result.stderr
    assert mode in result.stdout
