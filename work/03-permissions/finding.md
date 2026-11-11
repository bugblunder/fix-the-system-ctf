# Technical finding 03: Overly permissive service-state filesystem modes

> **AI-assisted engineering record.** This document is based on the supplied reference repair, source diff and retained automated lab evidence. It is not represented as an independently authored participant investigation. Facilitator review and scoring remain intentionally unfilled.

Participant ID: Not applicable — no participant investigation is claimed
Date / environment: 2026-11-11; Linux x86_64; Python 3.13.5; Fix the System CTF v2
Highest hint used: Reference solution / substantial ChatGPT assistance
Classification: CWE-732 (Incorrect Permission Assignment for Critical Resource) and CWE-276 (Incorrect Default Permissions)

## Scope and trust boundary

Affected component: `challenges/03-permissions`. The relevant trust boundary is between untrusted HTTP requesters or processes and protected application data/filesystem resources. The intended legitimate behavior is retained; the repair is not a blanket deny.

## Before-fix reproduction and observed impact

The baseline report records actual filesystem metadata: private directory 0755, private/service-state.json 0666, exchange directory 0777 and exchange/checkpoint.json 0666, both initially and after checkpoint creation. The report explicitly describes evidence as POSIX metadata plus current-user service I/O; it does not demonstrate a separate OS user's access.

- Baseline command executed by the native suite: `python3 tests/native_e2e.py --output-dir <evidence-dir>`; its baseline phase starts from a reset fixture and runs `python3 check.py --expect vulnerable --json ...`.
- Baseline run ID: `6b70a608-5ddb-454d-98a8-c15edf02c0d8`; source SHA-256: `1010cc810b4ec794497b4e3be3953801a8c65221e56280bfd2c01388ef04546b`; expected state: `vulnerable`; expectation met: `True`.
- Challenge 03 baseline gates: security=False, functionality=True, technical=False; baseline reproduced=True.
- Scoped evidence: [`before.json`](before.json). Full three-challenge report: [`../../evidence/native/baseline.json`](../../evidence/native/baseline.json).

## Root cause

The baseline assigned mode 0755 to the private directory, 0666 to the state file, 0777 to the exchange directory and 0666 to the checkpoint. This made private state and writable shared locations broader than required. Securing only the initial file is insufficient because the service creates a checkpoint later; newly created files inherit the process umask. Conversely, making the exchange directory private would break the lab's intended public status/exchange contract.

## Alternatives considered and rejected

| Alternative | Predicted security effect | Predicted functionality effect | Evidence / reason rejected |
| --- | --- | --- | --- |
| chmod only the initial state file | Initial file becomes private | Existing service still runs | Rejected: checkpoint creation creates a new file; tests inspect modes after checkpoint creation. |
| Set umask to 0000 | No permission regression | New files remain broadly accessible | Rejected: preserves the original unsafe creation behavior. |
| Make exchange directory 0700 | Restricts directory access | Breaks intended exchange/status behavior | Rejected: contract test `test_private_exchange_breaks_public_contract`. |
| Make every directory 0700 and every file 0600 | Strong default restriction | Can break required public traversal | Rejected in favor of distinct private and exchange policies with an explicit umask. |

## Repair and patch

The policy now sets the private directory to 0700, private state files to 0600, the exchange directory to 0755, and the process umask to 0077 so newly created files default to owner-only access. The exchange directory remains traversable for the intended service contract, while its new checkpoint file is restricted by the umask. The integration tests also verify the public status endpoint remains usable.

The challenge-specific diff is retained in [`patch.diff`](patch.diff).

## After-fix evidence and regression checks

- Fixed-state run ID: `917a3fd9-e4ff-4cf7-9420-3c86e13b53b9`; source SHA-256: `995911f993bd9826e2b5accafcbb9577365d04612f6b3657da6a120804eee32c`; expected state: `fixed`; expectation met: `True`.
- Challenge 03 fixed gates: security=True, functionality=True, technical=True; baseline reproduced in fixed state=False.
- Restart run ID: `eed39d5c-d19f-40f8-bbb1-70dd5fa4c274`; same source SHA-256: `995911f993bd9826e2b5accafcbb9577365d04612f6b3657da6a120804eee32c`; challenge gates after restart: security=True, functionality=True, technical=True.
- The final native `check.py --expect fixed --json` run ID was `4860887a-8c19-43bd-aba1-1e514e81ef90`, source SHA-256 `45b99110d90915f30d1dede7a4ec51128a4b11e1a40f7843a6029b173a38b62a`; technical flag: `FLAG{repair_03_cf9e17c97fa7}`.
- Evidence: [`after.json`](after.json), [`restart.json`](restart.json), and full reports under [`../../evidence/native/`](../../evidence/native/).

The native reference and restart reports show all security, functionality and technical gates passing for challenge 03. Tests check metadata for initial and newly created files, symlink handling, unsafe group-write settings and the public exchange contract. The evidence is limited to POSIX metadata and service I/O by the same UID; no second-UID access attempt was run.

This is not proof of complete multi-user isolation, ACL correctness, effective access through every ancestor directory, or behavior on native Windows/macOS. A production review should test with a separate OS identity and inspect ACLs, mount options, container capabilities and parent-directory permissions. This work was AI-assisted; no independent human investigation or reviewer score is claimed.

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
