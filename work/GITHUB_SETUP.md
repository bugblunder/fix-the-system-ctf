# Publish the prepared repository and record hosted CI

The local repository and tag are ready. No remote repository has been created,
no files have been pushed, and no hosted CI result is claimed.

In this session, the GitHub integration is disabled by the administrator and the
GitHub CLI is not authenticated. Complete the following on a machine/account
where you have authorized GitHub access. Do not put credentials in these files.

## Restore the prepared Git history

If you received the project as a Git bundle, follow the archive's START_HERE.md.
Clone the bundle instead of initializing a new repository; cloning preserves both
commits and the annotated `v2-baseline` tag.

## Publish to your intended destination

Create an empty GitHub repository in the intended account, with your chosen
visibility. Leave README/license/gitignore initialization off to avoid creating
unrelated history. Authenticate Git on your own machine through your normal method.

When cloning a bundle, `origin` initially points to that local bundle. Replace it
with your actual repository URL (the URL below is a placeholder):

```sh
git remote set-url origin https://github.com/OWNER/REPOSITORY.git
git push --set-upstream origin main
git push origin v2-baseline
```

For a repository with no existing `origin`, use `git remote add origin URL` instead.
These commands publish the prepared history; they do not create a GitHub repository.

## Verify the baseline run

The existing `.github/workflows/ci.yml` listens to pushes and manual dispatch.
In the repository's Actions tab, select the run for the **v2-baseline tag** and
verify its commit SHA against:

```sh
git rev-parse v2-baseline^{commit}
```

A passing run for a different commit is not a baseline run. If a tag push does
not start a run under your repository's settings, manually dispatch the existing
workflow with `v2-baseline` as the ref using the Actions UI or GitHub CLI:

```sh
gh workflow run ci.yml --ref v2-baseline
```

Wait for the actual result. Open the logs and download the
`native-validation-evidence` artifact. Confirm that it contains the contract log,
native run reports and summary, and inspect the exit codes and assertions. Retain
the download and record its location, run URL, run ID and tested SHA in CI_RECORD.md.
Leave the record pending if the run is blocked, fails, or has not been inspected.

Do not replace existing baseline evidence with hosted output or claim a pilot
from CI results; they answer different questions. Commit your completed CI record
once it is grounded in an actual hosted run.
