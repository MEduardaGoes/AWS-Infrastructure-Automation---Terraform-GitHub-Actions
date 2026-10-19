"""Reject sensitive Git-tracked paths without reading or printing file contents."""

import os
from pathlib import PurePosixPath
import subprocess
import sys


LOCK_FILE = "terraform/.terraform.lock.hcl"


def forbidden_reason(filename: str) -> str | None:
    path = PurePosixPath(filename.lower())
    name = path.name

    if ".terraform" in path.parts or ".aws" in path.parts:
        return "local Terraform data or AWS configuration"
    if name.endswith(".tfstate") or ".tfstate." in name:
        return "Terraform state"
    if name.endswith((".tfplan", ".plan", ".plan.json")) or ".tfplan." in name:
        return "saved Terraform plan"
    if name.endswith((".tfvars", ".tfvars.json", ".tfbackend")) or name == "backend.hcl":
        return "local variables or backend configuration"
    if name == ".env" or (name.startswith(".env.") and name != ".env.example"):
        return "local environment variables"
    if name.endswith((".pem", ".key", ".p12", ".pfx")) or name in {"id_rsa", "id_ed25519"}:
        return "private key or certificate bundle"
    if name in {".terraformrc", "terraform.rc", "override.tf", "override.tf.json"}:
        return "local Terraform configuration"
    if name.endswith(("_override.tf", "_override.tf.json")):
        return "local Terraform override"
    return None


def validate_files(filenames: list[str]) -> list[str]:
    errors = []
    if LOCK_FILE not in filenames:
        errors.append(f"Required provider lock file is not tracked: {LOCK_FILE}")
    for filename in filenames:
        reason = forbidden_reason(filename)
        if reason:
            errors.append(f"Forbidden tracked path ({reason}): {filename!r}")
    return errors


def main() -> int:
    result = subprocess.run(
        ["git", "ls-files", "--cached", "-z"],
        check=True,
        stdout=subprocess.PIPE,
    )
    filenames = [os.fsdecode(name) for name in result.stdout.split(b"\0") if name]
    errors = validate_files(filenames)
    for error in errors:
        print(error, file=sys.stderr)
    if errors:
        return 1
    print("Tracked-file guardrails passed; provider lock file is tracked.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
