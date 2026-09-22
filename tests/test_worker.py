import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from jusi_acp import ACPWorker
from jusi_gigacode.worker import create_worker, resolve_launch


def test_default_launch_uses_acp_and_browser_auth(tmp_path: Path, monkeypatch) -> None:  # type: ignore[no-untyped-def]
    monkeypatch.setattr("jusi_gigacode.worker.shutil.which", lambda command: "/tools/gigacode")
    launch = resolve_launch({"provider": "gigacode", "path": str(tmp_path)}, tmp_path)
    assert launch.argv == ("/tools/gigacode", "--acp")
    assert launch.cwd == tmp_path
    assert launch.auth_method == "gigacode"


def test_launch_maps_provider_options(tmp_path: Path, monkeypatch) -> None:  # type: ignore[no-untyped-def]
    monkeypatch.setattr("jusi_gigacode.worker.shutil.which", lambda command: "/tools/custom")
    launch = resolve_launch({
        "executable": "custom",
        "model": "coder-model",
        "approval_mode": "default",
        "arguments": ["--debug"],
        "environment": {"GIGACODE_PROFILE": "work"},
        "auth_method": "gigacode-login",
    }, tmp_path)
    assert launch.argv == (
        "/tools/custom", "--acp", "--model", "coder-model",
        "--approval-mode", "default", "--debug",
    )
    assert launch.environment == {"GIGACODE_PROFILE": "work"}
    assert launch.auth_method == "gigacode-login"


def test_auth_can_be_disabled_for_an_already_authenticated_install(tmp_path: Path, monkeypatch) -> None:  # type: ignore[no-untyped-def]
    monkeypatch.setattr("jusi_gigacode.worker.shutil.which", lambda command: "/tools/gigacode")
    assert resolve_launch({"auth_method": ""}, tmp_path).auth_method == ""


@pytest.mark.parametrize("configuration, message", [
    ({"unknown": True}, "unsupported GigaCode option"),
    ({"arguments": "--debug"}, "arguments must be an array"),
    ({"environment": []}, "environment must be a table"),
    ({"model": 7}, "model must be a string"),
])
def test_invalid_provider_configuration_is_rejected(
    tmp_path: Path, monkeypatch, configuration: dict, message: str
) -> None:  # type: ignore[no-untyped-def]
    monkeypatch.setattr("jusi_gigacode.worker.shutil.which", lambda command: "/tools/gigacode")
    with pytest.raises((TypeError, ValueError), match=message):
        resolve_launch(configuration, tmp_path)


def test_missing_executable_is_rejected(tmp_path: Path, monkeypatch) -> None:  # type: ignore[no-untyped-def]
    monkeypatch.setattr("jusi_gigacode.worker.shutil.which", lambda command: None)
    with pytest.raises(ValueError, match="not found on PATH"):
        resolve_launch({}, tmp_path)


def test_factory_returns_shared_worker_for_exact_provider() -> None:
    worker = create_worker(SimpleNamespace(plugin_id="gigacode"))
    try:
        assert isinstance(worker, ACPWorker)
        assert worker.provider.plugin_id == "gigacode"
    finally:
        worker.close()


def test_exact_worker_hands_authenticated_launch_to_shared_application(
    tmp_path: Path, monkeypatch
) -> None:  # type: ignore[no-untyped-def]
    monkeypatch.setattr("jusi_gigacode.worker.shutil.which", lambda command: "/tools/gigacode")
    worker = create_worker(SimpleNamespace(plugin_id="gigacode"))
    try:
        result = worker.handle("execute", {
            "alias": "work",
            "body": "continue after login",
            "cwd": str(tmp_path),
            "configuration": {"auth_method": "gigacode-login"},
            "additional_directories": [],
            "mcp_servers": [],
            "session_action": "new",
            "session_id": "",
        })
        surface = result.core_requests[0]
        payload = json.loads(Path(surface.argv[3]).read_text(encoding="utf-8"))
        assert payload["launch"] == {
            "argv": ["/tools/gigacode", "--acp"],
            "cwd": str(tmp_path),
            "environment": {},
            "auth_method": "gigacode-login",
        }
        assert payload["submission"]["body"] == "continue after login"
    finally:
        worker.close()
