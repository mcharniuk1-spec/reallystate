from __future__ import annotations

import unittest
from pathlib import Path

from bgrealestate.connectors.fixtures import fixture_dir, read_json, read_text
from bgrealestate.connectors.tier3 import OfficialRegisterWrapper, OperatorConsentRequired
from bgrealestate.source_registry import SourceRegistry


class TestTier3OfficialRegisterWrappers(unittest.TestCase):
    def test_official_register_templates_parse_redacted_response(self) -> None:
        repo_root = Path(__file__).resolve().parents[1]
        registry = SourceRegistry.from_file(repo_root / "data" / "source_registry.json")
        case_dir = fixture_dir("tier3_templates") / "official_register"
        raw_json_text = read_text(case_dir / "raw.json")
        expected = read_json(case_dir / "expected.json")

        for source_name in ("Property Register", "KAIS Cadastre"):
            with self.subTest(source_name=source_name):
                wrapper = OfficialRegisterWrapper(source_name, registry)
                actual = wrapper.parse_official_response(json_text=raw_json_text)
                expected_for_source = dict(expected)
                expected_for_source["source_name"] = source_name
                expected_for_source["reference_id"] = f"{source_name}:SYNTHETIC-ID-001"
                expected_for_source["verification_type"] = (
                    "parcel_validation" if source_name == "KAIS Cadastre" else "ownership_verification"
                )
                self.assertEqual(expected_for_source, actual)

    def test_live_query_requires_operator_consent(self) -> None:
        repo_root = Path(__file__).resolve().parents[1]
        registry = SourceRegistry.from_file(repo_root / "data" / "source_registry.json")
        wrapper = OfficialRegisterWrapper("Property Register", registry)
        with self.assertRaises(OperatorConsentRequired):
            wrapper.query_live(query={"parcel_or_property_id": "SYNTHETIC-ID-001"})


if __name__ == "__main__":
    unittest.main()
