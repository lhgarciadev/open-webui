import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from open_webui.utils.function_calling_mode import (
    model_builtin_tools_enabled,
    model_supports_native_function_calling,
    resolve_function_calling_mode,
    should_inject_builtin_tools,
)


def test_resolve_mode_uses_default_when_request_mode_missing():
    mode = resolve_function_calling_mode(
        metadata_params={},
        default_mode="native",
        model_supports_native=True,
    )
    assert mode == "native"


def test_resolve_mode_normalizes_invalid_mode_to_default():
    mode = resolve_function_calling_mode(
        metadata_params={"function_calling": "invalid-mode"},
        default_mode="native",
        model_supports_native=True,
    )
    assert mode == "default"


def test_resolve_mode_falls_back_to_default_when_model_has_no_native_support():
    mode = resolve_function_calling_mode(
        metadata_params={"function_calling": "native"},
        default_mode="native",
        model_supports_native=False,
    )
    assert mode == "default"


def test_model_capability_helpers():
    model = {"info": {"meta": {"capabilities": {"function_calling": False}}}}
    assert model_supports_native_function_calling(model) is False
    assert model_builtin_tools_enabled(model) is True


def test_builtin_tools_injection_gate():
    assert should_inject_builtin_tools("native", True) is True
    assert should_inject_builtin_tools("default", True) is False
    assert should_inject_builtin_tools("native", False) is False
