"""GigaCode launch validation and shared ACP worker construction."""
from __future__ import annotations

from collections.abc import Mapping
import os
from pathlib import Path
import shutil
from typing import Any

from jusi_acp import ACPWorker, AgentLaunch, ProviderSpec

from . import __version__

_COMMON_KEYS = {"provider", "path", "additional_directories", "mcp_servers"}
_PROVIDER_KEYS = {
    "executable", "arguments", "model", "approval_mode", "environment", "auth_method",
}


def resolve_launch(configuration: Mapping[str, Any], cwd: Path) -> AgentLaunch:
    """Validate one alias and construct a GigaCode ACP invocation."""
    unknown = sorted(set(configuration) - _COMMON_KEYS - _PROVIDER_KEYS)
    if unknown:
        raise ValueError(f"unsupported GigaCode option(s): {', '.join(unknown)}")

    executable = _string(configuration.get("executable", "gigacode"), "executable")
    resolved_executable = _resolve_executable(executable or "gigacode")
    arguments = _string_list(configuration.get("arguments", []), "arguments")

    argv = [resolved_executable, "--acp"]
    model = _string(configuration.get("model", ""), "model")
    if model:
        argv.extend(("--model", model))
    approval_mode = _string(configuration.get("approval_mode", ""), "approval_mode")
    if approval_mode:
        argv.extend(("--approval-mode", approval_mode))
    argv.extend(arguments)

    environment = configuration.get("environment", {})
    if not isinstance(environment, Mapping):
        raise TypeError("environment must be a table of string values")
    clean_environment: dict[str, str] = {}
    for key, value in environment.items():
        clean_key = _string(key, "environment name")
        clean_value = _string(value, f"environment value for {clean_key!r}", allow_empty=True)
        if not clean_key or "=" in clean_key:
            raise ValueError("environment names must be non-empty and cannot contain '='")
        clean_environment[clean_key] = clean_value

    # GigaCode is treated as a Qwen Code fork until its ACP handshake can be
    # inspected directly. Set auth_method = "" to disable automatic ACP auth,
    # or override it if GigaCode advertises another method ID.
    auth_method = _string(configuration.get("auth_method", "qwen-oauth"), "auth_method")
    return AgentLaunch(tuple(argv), cwd, clean_environment, auth_method)


def _resolve_executable(value: str) -> str:
    expanded = os.path.expanduser(value)
    if os.path.sep in expanded:
        path = Path(expanded).resolve()
        if not path.is_file():
            raise ValueError(f"GigaCode executable does not exist: {path}")
        if not os.access(path, os.X_OK):
            raise ValueError(f"GigaCode executable is not executable: {path}")
        return str(path)
    found = shutil.which(expanded)
    if found is None:
        raise ValueError(f"GigaCode executable {expanded!r} was not found on PATH")
    return found


def _string(value: Any, label: str, *, allow_empty: bool = True) -> str:
    if not isinstance(value, str):
        raise TypeError(f"{label} must be a string")
    if any(character in value for character in ("\x00", "\n", "\r")):
        raise ValueError(f"{label} contains an invalid control character")
    result = value.strip()
    if not allow_empty and not result:
        raise ValueError(f"{label} cannot be empty")
    return result


def _string_list(value: Any, label: str) -> list[str]:
    if not isinstance(value, list):
        raise TypeError(f"{label} must be an array of strings")
    return [_string(item, f"{label} item", allow_empty=False) for item in value]


PROVIDER = ProviderSpec("gigacode", __version__, resolve_launch)


def create_worker(context: Any) -> ACPWorker:
    return ACPWorker(context, PROVIDER)

