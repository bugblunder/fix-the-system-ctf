# Your investigation workspace

This directory provides structure only. The finding files are unfilled templates,
`patch.diff` files are empty, and before/after JSON files explicitly say NOT_RUN.
Nothing in this directory represents a completed personal contribution yet.
See [ASSISTED.md](../ASSISTED.md) for attribution boundaries.

## Before your first substantive commit

The Git history contains the unmodified release tagged `v2-baseline`, followed
by a separately identified assisted setup commit. Configure your own name/email:

```sh
git config user.name "YOUR NAME"
git config user.email "YOUR VERIFIED GIT EMAIL"
git switch -c work/challenge-01
```

Choose the actual name and email you want associated with your own contributions.
Do not relabel the baseline or setup history as independently authored work.

## Predict before testing

Fill in [BAD_FIX_PREDICTIONS.md](BAD_FIX_PREDICTIONS.md) with your own ideas and
predictions before you write/run the cases. Commit that prediction, then implement
and execute the experiment, save its output, and record the actual result in a
later commit. Keep incorrect predictions and explain what changed your reasoning.

## Evidence for a challenge

Each challenge directory contains `finding.md`, `patch.diff`, `before.json` and
`after.json`. Fill the finding from your observations and include alternatives
considered and rejected. No findings or patches have been written for you here.

For challenge 01, the sequence below captures evidence without providing a fix:

1. Stop any running lab. Run `python3 manage.py reset --challenge 01 --yes`.
2. Copy `fixtures/01.json` to `work/01-authorization/fixture.json` so the random
   inputs used in the paired reports can be identified. These are synthetic values.
3. Start `python3 run_lab.py --challenge 01` in another terminal.
4. Run the baseline check:

   ```sh
   python3 check.py --challenge 01 --expect vulnerable --json work/01-authorization/before.json
   ```

5. Stop the runner. Develop your own patch and record your reasoning. Restart it
   without another reset so the before/after comparison uses the same fixtures.
6. Run the fixed-state check, then preserve the challenge-only diff:

   ```sh
   python3 check.py --challenge 01 --json work/01-authorization/after.json
   git diff v2-baseline -- challenges/01-authorization > work/01-authorization/patch.diff
   ```

7. Capture a legitimate-operation example and repeat the fixed-state check after
   a further restart. Save that restart report under a separate filename.
8. Complete your finding and inspect `git diff` before committing. Include only
   the relevant challenge changes, your test additions, necessary fixture/evidence
   files and your notes. Keep unconnected challenge work separate.

Use the corresponding ID and path for 02 and 03. Do not reset between before/after
runs. If you do reset, capture a new baseline against the regenerated fixtures.
The existing release evidence is useful for comparison but does not replace your
own measured results. For 03, label mode observations separately from any future
real second-user experiment.

## Hosted CI

Follow [GITHUB_SETUP.md](GITHUB_SETUP.md), then fill [CI_RECORD.md](CI_RECORD.md)
from the actual run. The shipped workflow already uploads validation artifacts.
Do not add a passing badge before a corresponding hosted result exists.

## Pilot and completion

Run the [pilot protocol](../evaluation/PROTOCOL.md) only after the grader/tests
are settled. Record the release and commit given to participants. Keep real pilot
data separate from automated validation, with unfinished attempts and denominators.
The [results template](../evaluation/RESULTS_TEMPLATE.md) remains unfilled.

Review with `git log --oneline v2-baseline..HEAD` and inspect each commit. Being
able to explain a change from contemporaneous notes is a useful readiness test;
commit order alone does not establish authorship or understanding.
