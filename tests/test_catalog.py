from importlib.metadata import entry_points

from jusi.plugin_api import validate_catalog_claims
from jusi_acp import family_claim

from jusi_gigacode import __version__
from jusi_gigacode.catalog import catalog_entry


def test_catalog_is_an_exact_compatible_acp_provider() -> None:
    entry = catalog_entry()
    assert entry["plugin_id"] == "gigacode"
    assert entry["plugin_version"] == __version__
    assert entry["distribution"] == "jusi-gigacode"
    assert entry["families"] == [family_claim()]
    assert entry["kernel_extensions"] == ["jusi_gigacode.kernel"]
    assert entry["worker_entry_point"] == "jusi_gigacode.worker:create_worker"
    validate_catalog_claims({
        "protocol_version": 1,
        "catalog_version": 1,
        "discovery_id": "jusi_gigacode_tests",
        "plugins": [entry],
    })


def test_installed_distribution_exposes_exact_entry_point() -> None:
    matches = [item for item in entry_points(group="jusi.plugins.v1") if item.name == "gigacode"]
    if matches:
        assert matches[0].value == "jusi_gigacode.catalog:catalog_entry"

