# Solution guide — spoilers

Reference files live in `solutions/`. `manage.py solution --yes` installs them
and performs the exposure challenge's key rotation and backup removal. These are
instructor examples, not participant-authored findings.

## 01 · Enforce authorization at every object lookup

CWE-639 covers the caller-selected object identifier; CWE-915 describes the
additional uncontrolled field update. The baseline authenticates a caller but
permits every authenticated user to access any invoice. The receipt route has a
separate authorization bypass, and `invoice.update(body)` accepts protected fields.

The reference handles three separate decisions:

1. `can_access` permits the admin, the owning user, or a manager reading their
   team's invoices. Manager writes are forbidden, even within their team.
2. `app.py` enforces the same object decision after resolving either a direct ID
   or a receipt ID. Lists filter with the read decision.
3. `apply_patch` validates the complete request before any mutation: exactly one
   key, `note`, with a string of at most 200 characters. Mixed fields fail atomically.

Actor role/team come from the server's token mapping; ownership/team/amount belong
to server-side records. All five actor aliases are exercised over randomized
records. The checker verifies direct/indirect reads, writes, list scope, manager
boundaries, protected fields and unchanged state after denials. It restores notes
and baseline protected-field changes. Correlated denial and missing-resource logs
are part of grading; no bearer tokens may appear in the log.

Deny-all, admin-only, known-ID allowlists, manager writes, an indirect bypass and
an object-only patch without field validation are deliberately rejected by tests.
Randomized fixtures and multiple seeds are sampled property checks, not exhaustive
formal verification. Source review remains necessary.

## 02 · Contain publication, then remediate the leaked key

CWE-530/538 applies because the permitted download root includes private runtime
configuration and backups. The initial resolver already prevents escape from the
whole `site` directory; its boundary is simply too broad.

The reference resolves the requested target and checks containment beneath
`site/public`. Path containment uses `Path.is_relative_to`, not a string prefix.
This handles the tested symlink and parent-segment paths. The transport decodes
URLs once; double-encoded payloads remain filenames that do not exist.

Containment alone leaves a previously exposed key usable. The solution installer
creates a fresh 32-byte random key, writes it to the private runtime config, and
removes the deployed backup directory. Runtime configuration remains available to
the application. Old-key signatures fail verification; current-key signatures
succeed; a wrong signature is rejected. Public downloads and the catalog still
work. The grader also scans the deployed `site` files for old-key copies.

The signing/verification APIs are demonstrations and have no authorization role.
The fix does not claim to revoke a real user's session. Old synthetic keys remain
in trusted assessment fixtures and patch history; only deployment cleanup is
required here. Real incident-response scope could be wider.

The lab assumes no hostile concurrent filesystem writer. Check-then-open path
resolution is not a general solution to symlink replacement races. Native local
execution provides no container isolation.

## 03 · Repair existing modes and future file creation

CWE-732 describes the broad permission assignment. The vulnerable policy creates
state with `0666`, uses a writable shared directory, and applies `umask 0000`.
Changing only the initial state file leaves new checkpoint files exposed by mode.

Reference policy:

```json
{"directory_mode":"0700","file_mode":"0600","exchange_mode":"0755","umask":"0077"}
```

The private directory and state file retain owner access only. The exchange
directory stays searchable so its explicitly public `status.json` remains
readable. Newly created checkpoint files inherit `umask 0077`, which removes
group/other bits from the `0666` creation request. Replacing a checkpoint therefore
keeps it private without relying on a one-time chmod. Startup reapplies policy.

The checker inspects real modes/owners before and after checkpoint creation,
checks the public mode contract, and exercises actual service reads, increments,
checkpoint creation and restoration. Group-write policies, a permissive creation
mask, a read-only state file and a wholly private exchange directory fail the
appropriate gate. Missing state is an error.

This is an explicitly narrower contract than separate-UID runtime isolation.
The current-user process does not attempt to become a guest. The metadata policy
is intentionally strict even where a restrictive ancestor might mask a broad
file mode. Extended ACLs make this assessment inconclusive; they are reported as
errors. No setuid helper, privileged setup or simulated guest denial is used.

## Assessment boundary

Technical completion requires all security/functionality checks and no errors.
Written review remains pending until a person grades the finding. Flags and
source hashes are useful identifiers but forgeable on a participant-controlled
machine. A facilitator should provide a clean grader, vary fixture data, inspect
the patch and reject changes outside the permitted challenge surface.
