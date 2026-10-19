import unittest

from scripts.check_tracked_files import LOCK_FILE, forbidden_reason, validate_files


class RepositoryGuardrailTests(unittest.TestCase):
    def test_rejects_sensitive_paths_even_when_force_added(self):
        paths = [
            "terraform/terraform.tfstate",
            "terraform/terraform.tfstate.backup",
            "terraform/.terraform/providers/example",
            "terraform/deployment.tfplan",
            "terraform/deployment.tfplan.json",
            "terraform/deployment.plan",
            "terraform/deployment.plan.json",
            "terraform/production.tfvars",
            "terraform/production.tfvars.json",
            "terraform/local.tfbackend",
            "terraform/backend.hcl",
            ".env",
            "config/.env.production",
            ".aws/credentials",
            "keys/private.pem",
            "keys/private.key",
            "keys/id_ed25519",
            "terraform/local_override.tf",
            ".terraformrc",
            "terraform/PRODUCTION.TFVARS",
        ]
        for path in paths:
            with self.subTest(path=path):
                self.assertIsNotNone(forbidden_reason(path))
                self.assertTrue(validate_files([LOCK_FILE, path]))

    def test_allows_configuration_lock_and_sanitized_examples(self):
        paths = [
            LOCK_FILE,
            "terraform/main.tf",
            "terraform/backend.tf",
            "terraform/terraform.tfvars.example",
            ".env.example",
            ".github/workflows/ci.yml",
            "docs/validation.md",
        ]
        self.assertEqual(validate_files(paths), [])

    def test_requires_provider_lock_file(self):
        self.assertTrue(validate_files(["terraform/main.tf"]))

    def test_requires_the_correct_lock_file_path(self):
        self.assertTrue(validate_files(["other/.terraform.lock.hcl"]))

    def test_reports_all_forbidden_paths(self):
        self.assertEqual(len(validate_files([LOCK_FILE, ".env", "keys/private.pem"])), 2)


if __name__ == "__main__":
    unittest.main()
