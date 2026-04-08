from __future__ import annotations

import unittest


class TestConnectorFixtureHarness(unittest.TestCase):
    def test_fixture_harness_imports_without_optional_runtime(self) -> None:
        # Connector/fixture helpers must remain importable without forcing live network access.
        from bgrealestate.connectors.fixtures import fixture_dir  # noqa: F401
        from bgrealestate.connectors.protocol import Connector, DiscoveryResult  # noqa: F401


if __name__ == "__main__":
    unittest.main()

