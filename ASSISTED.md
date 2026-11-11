# Assistance and contribution record

Version 2 was developed with substantial AI assistance in this ChatGPT conversation.
The supplied applications, grader, tests, reference repairs, documentation and
creation-environment validation evidence form an **assisted baseline**. They must
not be presented as code or independent investigations authored solely by the
project owner. See the [v2 changelog](docs/CHANGELOG.md) and
[executed validation record](docs/BUILD_VALIDATION.md).

## Baseline and setup

- `v2-baseline` marks the exact, unchanged contents of the delivered v2 archive.
- Baseline commit: `d8a866f458f78619bf118b7bbdf29124da4f0dd1`.
- The subsequent setup commit adds this note and empty work/evidence templates.
  This setup was also AI-assisted; it is not an independent participant contribution.
- Import/setup commits use the neutral identity `Project setup <setup@example.invalid>`.
  This identifies an import operation, not a real person or the author of every file.
- Configure your own Git identity before making your own commits. Commit metadata
  alone does not establish independent authorship.

**Being after the baseline tag does not make a change independently authored.**
For each later contribution, record what you did, the reasoning and experiments,
and any assistance or reference solutions used. A reviewer should be able to
trace claims to the diff, contemporaneous notes and actual execution evidence.

## Evidence boundaries

The bundled automated results describe the runs documented in BUILD_VALIDATION.md.
The files under `work/` are unfilled templates, not additional findings, patches,
checker runs or participant results. Replace their explicit NOT_RUN placeholders
with actual output when you conduct the work.

Hosted GitHub CI has not been run during this setup, and no pilot results are
claimed. The current permission challenge assesses real filesystem metadata and
same-user service I/O, not access by a second OS account. Any future second-user
experiment must retain genuine identity and access-attempt evidence separately.
