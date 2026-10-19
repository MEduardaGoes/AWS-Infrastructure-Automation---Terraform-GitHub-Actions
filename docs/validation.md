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

The earlier Terraform CI was shown passing in GitHub Actions. After publishing
the simplified workflow, record its real workflow-run URL and commit identifier
here. Do not present local results as evidence of a deployed AWS environment.

## Security Guardrails Extension

The original CI has since been shown passing in GitHub Actions. The new guardrail
jobs were validated locally and still need their own GitHub execution after push.
See [security guardrail evidence](security-guardrails.md#validation-evidence) for
the tool versions, successful checks, and negative tests proving that an unsafe
workflow and a synthetic secret are rejected.

## S3-Focused Validation

After simplifying the project to S3 configuration security, local checks on
2026-10-19 confirmed:

- Terraform formatting, read-only-lock initialization, and validation passed.
- Five mocked AWS test scenarios passed.
- Five Python repository guardrail tests passed, and the tracked-file policy passed.
- Checkov 3.3.29 passed all six selected controls with no failures, skips, or parsing errors.
- Gitleaks 8.30.1 scanned five committed revisions with no secrets detected.
- actionlint 1.7.12 accepted the simplified workflow; shellcheck and pyflakes were disabled.
- Zizmor 1.31.1 reported no workflow findings with offline auditing.
- A temporary probe executed the actual Bash `CI Gate` in ten cases: all jobs
  succeeding, then each of the three required jobs failing, being cancelled, or
  being skipped. All nine non-success cases correctly failed the gate.

A separate local copy of `main.tf` was changed to `block_public_acls = false`.
Checkov rejected that copy with `CKV_AWS_53` and exit code 1: five controls passed
and one failed. The real project's configuration was not weakened or deployed.

The simplified workflow requires confirmation in a new GitHub Actions run after
publishing. No commit, push, AWS credentials, or cloud provisioning was used for
these local checks. The selected Checkov baseline does not represent a full
production audit, and provider mocks do not prove live AWS behavior.
