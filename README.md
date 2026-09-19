# jusi-gigacode

`jusi-gigacode` is the exact GigaCode provider for the shared Jusi ACP family.
It launches GigaCode over Agent Client Protocol while `jusi-acp` supplies the
`%%acp` magic, interactive VisiData application, permission choices, durable
follow-ups, cancellation, session controls, completion, and editor actions.

## Installation

Install this package, `jusi-acp`, and Jusi in the Python environment used by the
target Jupyter kernel. The `gigacode` executable must be available on that
target's `PATH`.

```bash
pip install jusi-gigacode
```

For development from sibling checkouts:

```bash
python3.12 -m venv .venv
.venv/bin/pip install -e ../jusi-acp -e '.[dev]'
.venv/bin/pytest
```

## Configuration

Add an ACP alias to `~/.jusi/jusi.toml` on the kernel target:

```toml
[acp.work]
provider = "gigacode"
path = "/path/to/project"
additional_directories = ["../shared"]
model = "provider-owned-model-name"
```

Then run:

```python
%%acp work
Inspect the project and implement the requested change.
```

The provider launches `gigacode --acp`. Until a direct GigaCode handshake is
available for conformance testing, GigaCode is treated as a Qwen Code fork.

Provider-specific alias options are:

- `executable`: executable name or path; defaults to `gigacode`.
- `model`: passed as `--model VALUE`.
- `approval_mode`: passed as `--approval-mode VALUE`. Leaving it unset allows
  ACP permission requests to reach the interactive Jusi client.
- `arguments`: an array of additional command-line arguments.
- `environment`: environment-variable overrides for the GigaCode process.
- `auth_method`: ACP authentication method ID. It defaults to `qwen-oauth`;
  set it to the ID advertised by GigaCode, or to an empty string to skip the
  proactive authentication call.

The executable inherits the target environment, including desktop/session
variables used by browser launchers. With the default authentication method,
`jusi-acp` calls ACP `authenticate` before creating the session. GigaCode owns
opening its authorization URL and waiting for the callback; after it completes,
the original cell body is submitted automatically.

Session controls and family commands include:

```python
%%acp work --load SESSION_ID
Replay and continue a stored session.
```

```python
%%acp work --resume SESSION_ID
Continue a stored session without replay.
```

Follow-up cells can use `/mode ID`, `/config ID VALUE`, `/auth METHOD_ID`, and
`/cancel`. Slash commands advertised by GigaCode are also completed and sent as
ordinary ACP prompts.

## GigaCode compatibility probe

The first live run should verify the authentication method ID and ACP protocol
version. If the default method is wrong, capture GigaCode's `initialize`
response—especially `protocolVersion`, `authMethods`, and `agentCapabilities`—
and configure the advertised method temporarily with `auth_method`.

