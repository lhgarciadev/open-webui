import json
import os
import subprocess
import sys
from pathlib import Path

import pytest


def _backend_dir() -> Path:
    return Path(__file__).resolve().parents[3]


def _extract_json_line(stdout: str) -> dict:
    for line in reversed(stdout.splitlines()):
        line = line.strip()
        if not line:
            continue
        try:
            return json.loads(line)
        except json.JSONDecodeError:
            continue
    raise AssertionError(f"No JSON payload found in subprocess output:\n{stdout}")


@pytest.mark.parametrize(
    "default_mode,model_supports_native,tool_ids,expected_mode,expect_builtin,expect_default_handler",
    [
        ("native", True, [], "native", True, False),
        ("default", True, ["custom"], "default", False, True),
        ("native", False, ["custom"], "default", False, True),
    ],
)
def test_process_chat_payload_function_calling_modes(
    default_mode: str,
    model_supports_native: bool,
    tool_ids: list[str],
    expected_mode: str,
    expect_builtin: bool,
    expect_default_handler: bool,
):
    env = os.environ.copy()
    env["PYTHONPATH"] = str(_backend_dir())

    script = f"""
import asyncio
import importlib.machinery
import json
import sys
import types
from types import SimpleNamespace
from unittest.mock import patch


class _Dummy:
    def __init__(self, *args, **kwargs):
        pass
    def __call__(self, *args, **kwargs):
        return _Dummy()
    def __getattr__(self, _name):
        return _Dummy()
    def __iter__(self):
        return iter(())


torch_stub = types.ModuleType("torch")
torch_stub.__spec__ = importlib.machinery.ModuleSpec("torch", loader=None)
torch_stub.Tensor = _Dummy
torch_stub.dtype = _Dummy
torch_stub.backends = types.SimpleNamespace(
    mps=types.SimpleNamespace(is_available=lambda: False, is_built=lambda: False)
)
torch_stub.cuda = types.SimpleNamespace(is_available=lambda: False)
torch_stub.__getattr__ = lambda _name: _Dummy()
sys.modules["torch"] = torch_stub

from open_webui.utils import middleware as m


async def run_case():
    async def event_emitter(_evt):
        return None

    async def no_op_async(*_args, **_kwargs):
        return None

    async def pipeline_stub(request, form_data, user, models):
        return form_data

    async def filters_stub(**kwargs):
        return kwargs["form_data"], {{}}

    async def files_stub(request, form_data, extra_params, user):
        return form_data, {{"sources": []}}

    async def tools_handler_stub(request, form_data, extra_params, user, models, tools_dict):
        form_data["_default_tools_handler_called"] = True
        return form_data, {{"sources": []}}

    async def get_tools_stub(request, tool_ids, user, context):
        return {{"custom_tool": {{"spec": {{"name": "custom_tool", "parameters": {{}}}}}}}}

    req = SimpleNamespace(
        cookies={{}},
        app=SimpleNamespace(
            state=SimpleNamespace(
                oauth_manager=SimpleNamespace(get_oauth_token=no_op_async),
                config=SimpleNamespace(
                    DEFAULT_FUNCTION_CALLING_MODE={default_mode!r},
                    TASK_MODEL=None,
                    TASK_MODEL_EXTERNAL=None,
                    VOICE_MODE_PROMPT_TEMPLATE="",
                    CODE_INTERPRETER_PROMPT_TEMPLATE="",
                    TOOL_SERVER_CONNECTIONS=[],
                ),
                MODELS={{"test-model": {{"id": "test-model"}}}},
            )
        ),
        state=SimpleNamespace(direct=False),
    )

    user = SimpleNamespace(id="u1")
    form_data = {{
        "model": "test-model",
        "messages": [{{"role": "user", "content": "hola"}}],
        "features": {{}},
        "tool_ids": {tool_ids!r},
    }}
    metadata = {{"params": {{}}}}
    model = {{
        "id": "test-model",
        "info": {{
            "meta": {{
                "capabilities": {{
                    "function_calling": {model_supports_native!r},
                    "builtin_tools": True,
                    "file_context": False,
                }}
            }}
        }},
    }}

    with patch.object(m, "apply_params_to_form_data", lambda fd, mdl: fd), \
         patch.object(m, "get_system_message", lambda messages: None), \
         patch.object(m, "get_event_emitter", lambda metadata: event_emitter), \
         patch.object(m, "get_event_call", lambda metadata: None), \
         patch.object(m, "get_task_model_id", lambda *args, **kwargs: "test-model"), \
         patch.object(m, "get_last_user_message", lambda messages: "hola"), \
         patch.object(m, "process_pipeline_inlet_filter", pipeline_stub), \
         patch.object(m, "get_sorted_filter_ids", lambda *args, **kwargs: []), \
         patch.object(m, "process_filter_functions", filters_stub), \
         patch.object(m, "get_tools", get_tools_stub), \
         patch.object(m, "get_builtin_tools", lambda *args, **kwargs: {{"builtin_now": {{"spec": {{"name": "builtin_now", "parameters": {{}}}}}}}}), \
         patch.object(m, "add_file_context", lambda messages, chat_id, user: messages), \
         patch.object(m, "chat_completion_files_handler", files_stub), \
         patch.object(m, "chat_completion_tools_handler", tools_handler_stub):
        out_form_data, out_metadata, _ = await m.process_chat_payload(
            req, form_data, user, metadata, model
        )

    out = {{
        "mode": out_metadata.get("params", {{}}).get("function_calling"),
        "builtin_injected": any(
            t.get("function", {{}}).get("name") == "builtin_now"
            for t in out_form_data.get("tools", [])
        ),
        "default_handler_called": bool(out_form_data.get("_default_tools_handler_called", False)),
    }}
    print(json.dumps(out))


asyncio.run(run_case())
"""

    result = subprocess.run(
        [sys.executable, "-c", script],
        env=env,
        capture_output=True,
        text=True,
        timeout=90,
    )

    assert result.returncode == 0, result.stderr
    payload = _extract_json_line(result.stdout)
    assert payload["mode"] == expected_mode
    assert payload["builtin_injected"] is expect_builtin
    assert payload["default_handler_called"] is expect_default_handler
