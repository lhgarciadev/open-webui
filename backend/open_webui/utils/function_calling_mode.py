"""Utilities for resolving function calling mode behavior.

This module is intentionally dependency-light so it can be unit-tested
without importing the full backend runtime.
"""

from typing import Any


VALID_FUNCTION_CALLING_MODES = ("native", "default")


def model_supports_native_function_calling(model: dict[str, Any]) -> bool:
    """Return whether model metadata explicitly disables native function calling."""
    return (
        model.get("info", {})
        .get("meta", {})
        .get("capabilities", {})
        .get("function_calling", True)
    )


def model_builtin_tools_enabled(model: dict[str, Any]) -> bool:
    """Return whether model metadata allows builtin tools injection."""
    return (
        model.get("info", {})
        .get("meta", {})
        .get("capabilities", {})
        .get("builtin_tools", True)
    )


def resolve_function_calling_mode(
    metadata_params: dict[str, Any] | None,
    default_mode: str,
    model_supports_native: bool,
) -> str:
    """Resolve effective function-calling mode using request, app default and capability fallback."""
    mode = (metadata_params or {}).get("function_calling")
    if not mode:
        mode = default_mode or ""

    if mode not in VALID_FUNCTION_CALLING_MODES:
        mode = "default"

    if mode == "native" and not model_supports_native:
        return "default"

    return mode


def should_inject_builtin_tools(function_calling_mode: str, builtin_tools_enabled: bool) -> bool:
    return function_calling_mode == "native" and builtin_tools_enabled
