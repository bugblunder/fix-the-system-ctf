# Technical finding 02: Private files and compromised signing key exposed

> **AI-assisted engineering record.** This document is based on the supplied reference repair, source diff and retained automated lab evidence. It is not represented as an independently authored participant investigation. Facilitator review and scoring remain intentionally unfilled.

Participant ID: Not applicable — no participant investigation is claimed
Date / environment: 2026-11-11; Linux x86_64; Python 3.13.5; Fix the System CTF v2
Highest hint used: Reference solution / substantial ChatGPT assistance
Classification: CWE-552 (Files or Directories Accessible to External Parties) and CWE-22 (Improper Limitation of a Pathname to a Restricted Directory)

## Scope and trust boundary

Affected component: `challenges/02-exposure`. The relevant trust boundary is between untrusted HTTP requesters or processes and protected application data/filesystem resources. The intended legitimate behavior is retained; the repair is not a blanket deny.

## Before-fix reproduction and observed impact

The baseline checker report records successful serving of `private/runtime.json`, `backups/runtime.json.bak`, URL-encoded and traversal variants, and acceptance of the old signing key. The report's `baseline_witnesses` for challenge 02 confirm the private file, backup and old key were exposed/valid. Legitimate public download and catalog functionality passed in the vulnerable baseline.

- Baseline command executed by the native suite: `python3 tests/native_e2e.py --output-dir <evidence-dir>`; its baseline phase starts from a reset fixture and runs `python3 check.py --expect vulnerable --json ...`.
- Baseline run ID: `6b70a608-5ddb-454d-98a8-c15edf02c0d8`; source SHA-256: `1010cc810b4ec794497b4e3be3953801a8c65221e56280bfd2c01388ef04546b`; expected state: `vulnerable`; expectation met: `True`.
- Challenge 02 baseline gates: security=False, functionality=True, technical=False; baseline reproduced=True.
- Scoped evidence: [`before.json`](before.json). Full three-challenge report: [`../../evidence/native/baseline.json`](../../evidence/native/baseline.json).

## Root cause

The original download policy confined paths to the site root, but the root included both `public` and `private` content, as well as the backup directory. A root-containment check is therefore weaker than a public-document-root check. A backup retained an old signing key, and the deployed private configuration still used that key, so removing only the route or blocking a filename would not revoke the compromised credential.

## Alternatives considered and rejected

| Alternative | Predicted security effect | Predicted functionality effect | Evidence / reason rejected |
| --- | --- | --- | --- |
| Block a few sensitive filenames/extensions | Known names may be denied | Public downloads continue | Rejected: encoded paths, traversal variants and new filenames bypass a narrow blocklist; contract test `test_backup_only_blocklist_fails`. |
| Confine paths to the site root | Prevents escaping the site | Public and private files remain reachable | Rejected: private and backup directories are inside the site root; contract tests cover symlinks and encoded traversal. |
| Disable all downloads | Prevents file disclosure | Breaks the public guide feature | Rejected: `test_block_all_downloads_breaks_feature`. |
| Rotate the key but retain the backup | New config key differs | Signing service still functions | Rejected: backup remains a second copy of the compromised secret; `test_rotation_without_removing_backup_fails`. |

## Repair and patch

`resolve_public` resolves both the public root and candidate to canonical paths and permits a download only when the candidate is a file beneath the canonical `site/public` directory. The backup containing the old key was deleted, and the signing key in the private runtime configuration was rotated. These changes address both the disclosure path and the credential compromise; path filtering alone would not be sufficient.

The challenge-specific diff is retained in [`patch.diff`](patch.diff).

## After-fix evidence and regression checks

- Fixed-state run ID: `917a3fd9-e4ff-4cf7-9420-3c86e13b53b9`; source SHA-256: `995911f993bd9826e2b5accafcbb9577365d04612f6b3657da6a120804eee32c`; expected state: `fixed`; expectation met: `True`.
- Challenge 02 fixed gates: security=True, functionality=True, technical=True; baseline reproduced in fixed state=False.
- Restart run ID: `eed39d5c-d19f-40f8-bbb1-70dd5fa4c274`; same source SHA-256: `995911f993bd9826e2b5accafcbb9577365d04612f6b3657da6a120804eee32c`; challenge gates after restart: security=True, functionality=True, technical=True.
- The final native `check.py --expect fixed --json` run ID was `4860887a-8c19-43bd-aba1-1e514e81ef90`, source SHA-256 `45b99110d90915f30d1dede7a4ec51128a4b11e1a40f7843a6029b173a38b62a`; technical flag: `FLAG{repair_02_f5b56613ca46}`.
- Evidence: [`after.json`](after.json), [`restart.json`](restart.json), and full reports under [`../../evidence/native/`](../../evidence/native/).

The native reference and restart reports show all security, functionality and technical gates passing for challenge 02. Regression tests include path traversal, double encoding, symlink containment, backup retention, old-key revocation, and preservation of legitimate public downloads and signing/verification behavior.

A production deployment should store signing keys in a secrets manager or KMS, audit all historical copies and deployment artifacts, invalidate any derived credentials/tokens as appropriate, and ensure the web server has no alternate static-file route exposing private directories. This work was AI-assisted; the recorded evidence is automated lab output, not a personal manual reproduction.

## Facilitator review — pending independent reviewer

| Criterion | Score |
| --- | --- |
| Reproduction and impact | Pending /2 |
| Root cause and classification | Pending /3 |
| Repair rationale | Pending /2 |
| Regression evidence | Pending /2 |
| Clarity and limits | Pending /1 |
| Total | Pending /10 |

Technical gates verified from trusted grader: **Yes — automated technical gates passed**
Accepted as full completion: **Pending facilitator decision**
Reviewer / date / feedback: Pending
