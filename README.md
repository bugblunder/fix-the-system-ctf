# Fix the System to Capture the Flag

**Can you repair a vulnerability while preserving the application's intended behavior?**

A three-challenge defensive CTF for a 4–6 week project. Find the issue, demonstrate
its impact, explain its root cause, repair it, and pass separate security and
functionality checks. Disabling the feature does not earn completion.

**Version 2 runs locally with Python. No Docker, administrator account, package
installation, or external service is required.** Use Python 3.10+ on Linux, or
WSL2 on Windows. Keep the project in the Linux filesystem, such as
`~/projects/fix-the-system-ctf`; Windows-mounted drives may not preserve the
permission semantics used by challenge 03. Validation was performed on Linux
with Python 3.12.14; WSL itself has not been tested here.

| Challenge | Root cause | Security contract after repair | Behavior that must remain |
| --- | --- | --- | --- |
| 01 · Whose invoice? | Missing object authorization (CWE-639) and unsafe field binding (CWE-915) | Per-user and team scope on lists, direct IDs and indirect receipts; no forbidden writes or protected-field changes; correlated denial logs | Owners read/update their invoices; manager reads team invoices; admin manages all; only notes are editable |
| 02 · The forgotten backup | Private tree and backup exposure (CWE-530/538) | Private paths blocked, exposed key rotated and old signatures rejected, backup and old-key copies removed from the deployed site | Public files download; runtime catalog, signing and verification still work |
| 03 · Who can touch this file? | Incorrect file/directory permissions and creation policy (CWE-732) | Actual file modes meet the documented policy, including after checkpoint creation; private files have no group/other permissions | Current-user service reads/writes/checkpoints; public status retains read and traversal permissions |

**Challenge 03 is a filesystem-policy assessment.** The checker inspects real
Linux file metadata and performs real service I/O as the current user. It does
**not** launch a second OS user or prove cross-user isolation. This replaces the
old container/UID test with a smaller contract that can be executed without
privileges. The central repair-plus-behavior research question remains intact.

## Start

From the extracted project directory, in terminal 1:

```sh
python3 manage.py reset --yes
python3 run_lab.py
```

In terminal 2, from the same directory:

```sh
python3 check.py --expect vulnerable --json reports/before.json
```

Expected: security FAIL, functionality PASS, and `Expected vulnerable: PASS`
(exit 0). That reproduces the intended defects; it does not mean they are fixed.
The services listen on [8101](http://127.0.0.1:8101),
[8102](http://127.0.0.1:8102), and [8103](http://127.0.0.1:8103), all loopback only.

Read [the participant guide](docs/PARTICIPANT_GUIDE.md). Stop the runner with
Ctrl+C, edit `challenges/`, restart it, then run:

```sh
python3 check.py --json reports/after.json
```

Both automated gates must pass. Submit a written finding using
[submissions/TEMPLATE.md](submissions/TEMPLATE.md); human review remains required.
Flags are readable, locally generated completion markers, not evidence of
independent authorship or tamper-resistant awards.

Select one challenge with `--challenge 01` on both runner and checker. Use
`--port-base 9100` on both to change the three ports to 9101–9103. No network
connections beyond local requests are needed to run the project.

## Reset and reference repairs

Stop the runner first. Reset saves your prior source and fixtures under
`reports/patch-backups/`, restores starter code, and regenerates IDs, amounts,
receipt references, tokens and demo secrets. Restarting alone does not reset
source files or regenerate credentials.

```sh
python3 manage.py reset --challenge 01 --yes
python3 run_lab.py
```

For an instructor reference run (spoilers):

```sh
python3 manage.py reset --yes
python3 manage.py solution --yes
python3 run_lab.py
```

Run `python3 check.py` from another terminal. The solution installer applies
reference code, rotates the demonstration signing key, and removes the active
backup. Reset first if other participant changes are present. Reset/solution
commands refuse to modify a project while its runner holds the project lock.
`--seed 91` reproduces randomized fixture structure; tokens and keys remain fresh.

## Validation

```sh
python3 tests/validate.py --output-dir reports/my-validation
```

This runs HTTP/filesystem regression tests and a full native launcher/checker
exercise in disposable copies. It checks baseline → repair → restart → reset,
rejects broken fixes, distinguishes missing-file errors, preserves checker-modified
state, and confirms that the runner releases its ports. It does not alter your
challenge edits. Keep the returned logs and JSON as evidence.

See [BUILD_VALIDATION.md](docs/BUILD_VALIDATION.md) and the actual results under
[`evaluation/validation/`](evaluation/validation/). GitHub Actions is configured
for the same command and artifact upload; no hosted CI run is claimed here.

## Layout

| Path | Purpose |
| --- | --- |
| `run_lab.py`, `lab/` | Loopback processes, logging, transport and synthetic fixture generation |
| `challenges/` | Participant-editable implementations and demo data |
| `baselines/`, `solutions/` | Reset copies and instructor reference repairs |
| `fixtures/` | Generated assessment inputs; outside participant edit scope |
| `check.py`, `grader/` | Independent security/functionality checks |
| `tests/` | Bad-fix regressions, randomized cases and native integration |
| `docs/` | Guides, hints, rubric, project plan and limitations |
| `evaluation/` | Executed automated evidence and a separate, unfilled pilot protocol |
| `submissions/` | Required finding template |

## Scope and honest claims

Use synthetic data and run as a regular account on your own machine. These are
ordinary local processes, without container isolation; keep them loopback-bound.
The built-in HTTP server is a teaching component, not a production server.

The trusted assessment includes the grader, fixture generator, launcher and
shared transport. Randomization and bad-fix tests make sample-specific patches
less useful, but a participant who controls the checker or reads the fixtures
can still game a local lab. A reviewer must inspect the submitted patch and run a
trusted checker. Finite tests do not prove universal security.

This release is an assisted implementation. It is not evidence that you independently
authored the supplied code or completed a classmate study. Build your portfolio
claim from the investigations, patches, explanations and measured validation you
actually perform. Follow [PROJECT_PLAN.md](docs/PROJECT_PLAN.md).
