import ast
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class DatabaseModelTests(unittest.TestCase):
    def test_sqlalchemy_model_file_is_syntax_valid_without_dependencies_installed(self) -> None:
        models = ROOT / "src" / "bgrealestate" / "db" / "models.py"
        ast.parse(models.read_text(encoding="utf-8"))

    def test_model_foundation_covers_core_mvp_areas(self) -> None:
        model_text = (ROOT / "src" / "bgrealestate" / "db" / "models.py").read_text(encoding="utf-8")
        for class_name in [
            "SourceRegistryModel",
            "SourceLegalRuleModel",
            "CrawlJobModel",
            "RawCaptureModel",
            "SourceListingModel",
            "CanonicalListingModel",
            "PropertyEntityModel",
            "PropertyOfferModel",
            "MediaAssetModel",
            "BuildingEntityModel",
            "AppUserModel",
            "OrganizationAccountModel",
            "LeadThreadModel",
            "LeadMessageModel",
            "PublishJobModel",
            "PublishAttemptModel",
        ]:
            self.assertIn(f"class {class_name}", model_text)

    def test_db_package_does_not_import_sqlalchemy_on_package_import(self) -> None:
        init_text = (ROOT / "src" / "bgrealestate" / "db" / "__init__.py").read_text(encoding="utf-8")
        self.assertNotIn("from .models import", init_text)


if __name__ == "__main__":
    unittest.main()
