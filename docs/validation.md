# Local Validation Evidence

Date: 2026-10-19 (America/Sao_Paulo).

These are local results, not a GitHub Actions execution or AWS deployment.

| Check | Tool | Result |
| --- | --- | --- |
| `terraform fmt -check -recursive` | Terraform 1.16.6 | Passed |
| `terraform -chdir=terraform init -backend=false -lockfile=readonly -input=false -no-color` | AWS provider 6.69.1 | Passed |
| `terraform -chdir=terraform validate -no-color` | Terraform 1.16.6 | Configuration valid |
| `terraform -chdir=terraform test -no-color` | Terraform 1.16.6 | Five scenarios passed, zero failed |
| `checkov --config-file .checkov.yml` | Checkov 3.3.29 | Six checks passed, zero failed, zero skipped |
| `actionlint -shellcheck= -pyflakes= .github/workflows/ci.yml` | actionlint 1.7.12 | Passed |

Test scenarios:

- Secure storage defaults: encryption, versioning, public access block, HTTP-deny policy, and disabled force deletion.
- Custom project, environment, and region inputs.
- Rejection of an invalid project name.
- Rejection of an invalid environment.
- Rejection of an invalid region format.

All Terraform test runs use a mocked AWS provider and `command = plan`. No AWS
credentials, real provider planning, `apply`, or `destroy` were used. The provider
schema and dependencies were downloaded, but no cloud resources were created.

Terraform and actionlint downloads were verified against official SHA-256
checksums. Checkov ran in a temporary Python environment, using the same Checkov
version selected by the pinned CI action. No tools were installed globally.

The actionlint check did not run shellcheck or pyflakes. Mock tests do not verify
AWS permissions, actual S3 behavior, account policies, remote state, or OIDC.
Checkov covered the six explicitly selected controls, not its full policy set.

The GitHub workflow has not been executed by this session. After publishing,
record the real workflow-run URL and commit identifier here. Do not present these
local results as evidence of a deployed AWS environment.

## Security Guardrails Extension

The original CI has since been shown passing in GitHub Actions. The new guardrail
jobs were validated locally and still need their own GitHub execution after push.
See [security guardrail evidence](security-guardrails.md#validation-evidence) for
the tool versions, successful checks, and negative tests proving that an unsafe
workflow and a synthetic secret are rejected.
