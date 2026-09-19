"""Exact-provider attestation backed by the shared ACP kernel dispatcher."""

from jusi_acp import KernelProviderAdapter

from . import __version__

_adapter = KernelProviderAdapter("gigacode", __version__)

jusi_kernel_adapter_v1 = _adapter.manifest
configure_jusi_runtime_v1 = _adapter.configure
load_ipython_extension = _adapter.load_ipython_extension

