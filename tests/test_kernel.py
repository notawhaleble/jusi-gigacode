from jusi_gigacode import __version__
from jusi_gigacode.kernel import jusi_kernel_adapter_v1


def test_kernel_attests_exact_provider_and_family() -> None:
    assert jusi_kernel_adapter_v1() == {
        "plugin_id": "gigacode",
        "plugin_version": __version__,
        "families": [{"family_id": "acp", "magic_name": "acp"}],
    }

