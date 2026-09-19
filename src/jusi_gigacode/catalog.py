"""Side-effect-free Jusi catalog entry for the exact GigaCode provider."""
from __future__ import annotations

from typing import Any

from . import __version__


def catalog_entry() -> dict[str, Any]:
    # Keep this claim byte-for-byte compatible with jusi_acp.family_claim().
    # Discovery must not import the worker or start the ACP application.
    return {
        "plugin_id": "gigacode",
        "plugin_version": __version__,
        "distribution": "jusi-gigacode",
        "families": [{
            "family_id": "acp",
            "magic_name": "acp",
            "capabilities": ["execute", "followup", "complete", "interrupt", "editor_actions"],
            "presentation": {"syntax": "markdown", "indent": "markdown"},
        }],
        "kernel_extensions": ["jusi_gigacode.kernel"],
        "worker_entry_point": "jusi_gigacode.worker:create_worker",
        "media_types": ["text/x-ansi"],
        "interaction": "terminal_interactive",
    }

