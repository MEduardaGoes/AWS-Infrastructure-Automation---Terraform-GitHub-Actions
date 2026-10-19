# Pipeline Security Guardrails

## Blocking Checks

The workflow first runs `Security Guardrails`. Terraform checks and the S3
Checkov baseline run only after that job succeeds. The final `CI Gate` requires
all three validation jobs to succeed; failures, cancellations, or skipped dependencies do
not count as approval. No job uses `continue-on-error`.

| Guardrail | What it blocks |
| --- | --- |
| Tracked-file policy | State files, saved plans, local variables, environment files, private key filenames, and local AWS/Terraform configuration |
| Required lock file | Removing `terraform/.terraform.lock.hcl` from version control |
| Gitleaks 8.30.1 | Detected secrets anywhere in the fetched Git history |
| Zizmor 1.31.1 | Workflow findings of low or higher severity and confidence, such as unsafe expressions and unpinned actions |
| Existing Terraform and Checkov checks | Invalid configuration, failed mocked tests, or failed S3 baseline controls |

Gitleaks uses its built-in rules and scans full fetched history, with findings
fully redacted in logs. Its Linux binary version and archive SHA-256 are pinned.
No Gitleaks account, action license, AWS credentials, or user-supplied secret is
required. Zizmor online audits and SARIF uploads are disabled, so the job needs
only read access to repository contents. Rules requiring GitHub API access are
outside this configuration's scope.

Actions remain pinned by commit SHA. Runners use `ubuntu-24.04` to avoid silent
OS migrations from the `ubuntu-latest` label. Timeouts, disabled persisted
checkout credentials, and read-only default token permissions remain enabled.
The final gate needs no repository permissions. The project validates an S3
configuration without provisioning resources or requiring AWS credentials.

## Make the Gate Required on GitHub

After publishing these changes and confirming a successful run:

1. Open repository Settings, then Rules and Rulesets (or branch protection).
2. Target `main` and require a pull request before merging.
3. Enable required status checks and select the `CI Gate` check from this workflow.
4. Require the branch to be up to date, and restrict bypass/direct-push access
   according to your repository's collaboration needs.

These repository settings have not been configured by this code change. Without
a required-check rule, CI reports a failure but cannot itself prevent a merge.
Protect review of workflow and policy changes as well: a contributor able to
change the checks can weaken them. CODEOWNERS enforcement can be added when
there is another maintainer available to review sensitive changes.

## Run Locally

From the repository root, using Python 3.10 or newer:

```powershell
python -m unittest discover -s tests -v
python scripts/check_tracked_files.py
gitleaks git --redact=100 --no-banner --log-opts="--all" .
zizmor --offline --min-severity low --min-confidence low .github/workflows
```

The file policy inspects the Git index, not untracked files. It catches forbidden
files even if they were added with `git add -f`, but filename rules cannot detect
every secret or sensitive document. `.tfvars.example` and `.env.example` are
allowed only for sanitized examples. Gitleaks complements those filename checks;
its built-in rules also have detection limits.

Never use real credentials to demonstrate a failure. If a real credential is
detected, revoke or rotate it first; deleting the current file does not remove
the secret from Git history. Do not disable the scan merely to get a green build.

## Validation Evidence

Local validation completed on 2026-10-19:

- Five Python guardrail tests passed, including 20 forbidden-path cases.
- The tracked-file policy passed against the current Git index.
- Gitleaks 8.30.1 scanned three local commits with no secrets detected.
- Gitleaks rejected a generated synthetic token with exit code 1; no real token
  was used, stored in the repository, or printed in logs.
- Zizmor 1.31.1 reported no findings for the updated workflow.
- Zizmor rejected a temporary unsafe fixture containing an unpinned action and
  attacker-controlled shell interpolation.
- actionlint 1.7.12 accepted the workflow; shellcheck and pyflakes were disabled.

Tools were downloaded temporarily and checked against official SHA-256 digests.
The historical Gitleaks scan covers committed files, not the pending changes.
The next push will scan the commit containing these changes as well. The previous
successful GitHub run predates these guardrails; a new GitHub run is required to
confirm their Linux CI execution. No cloud resources are provisioned by them.

## References

- [Gitleaks](https://github.com/gitleaks/gitleaks)
- [Zizmor usage](https://docs.zizmor.sh/usage/)
- [Zizmor action](https://github.com/zizmorcore/zizmor-action)
