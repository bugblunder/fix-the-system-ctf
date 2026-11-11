# Participant guide

Work only on this local, synthetic-data lab. Edit `challenges/`; keep `lab/`,
`grader/`, fixtures, runner and tests trusted. Stop the runner before changing
code or resetting. Reset preserves a snapshot; restarting clears invoice/counter
state but keeps source edits and fixture IDs.

For each challenge: save baseline JSON; demonstrate the problem; explain the
trust boundary; make a general repair; restart; save fixed JSON and a legitimate
operation; repeat after another restart; submit the finding template.

## 01 · Whose invoice?

Inspect the generated IDs and demonstration credentials:

```sh
python3 -m json.tool fixtures/01.json
```

| Actor | Read scope | Write scope |
| --- | --- | --- |
| Alice, Bob, Casey | Own invoices | Own notes only |
| Manager | North-team invoices (Alice and Casey) | None |
| Admin | All invoices | All notes; no ownership, team or amount changes |

Invoice IDs, actor IDs, amounts, receipt IDs and tokens change at reset. Replace
`TOKEN`, `ID` and `RECEIPT` below with current fixture values:

```sh
curl -i -H 'Authorization: Bearer TOKEN' http://127.0.0.1:8101/api/invoices/ID
curl -i -H 'Authorization: Bearer TOKEN' http://127.0.0.1:8101/api/receipts/RECEIPT
curl -i -X PATCH -H 'Authorization: Bearer TOKEN' -H 'Content-Type: application/json' -d '{"note":"Delivery instructions"}' http://127.0.0.1:8101/api/invoices/ID
```

Compare own versus foreign records, direct versus receipt lookup, and a manager's
read versus write. Inspect both the policy and its call sites. Try an update
containing a valid note plus a protected field; the entire update must be rejected
without changing the note or other fields. Only a string note of at most 200
characters is editable. Do not hardcode fixture values.

Every denied known-object request must produce an `authorization_denied` JSON
log with actor, resource, method and request ID. A missing ID produces
`resource_not_found`, distinguishable from a denial even when the response uses
404. Logs are in `reports/live/01.log`; bearer tokens must be absent. The checker
uses random request IDs to correlate the exact requests it sent.

## 02 · The forgotten backup

The intended public tree is `site/public`. Runtime configuration is private;
the backup contains the same initially exposed signing key.

```sh
curl -i http://127.0.0.1:8102/files/public/guide.txt
curl -i http://127.0.0.1:8102/files/backups/runtime.json.bak
curl -i http://127.0.0.1:8102/files/private/runtime.json
curl -i http://127.0.0.1:8102/api/catalog
```

The toy signing API accepts `POST /api/sign` with `{"message":"demo"}`. Verification
accepts `POST /api/verify` with message and signature and returns `{"valid":true}`
or false. These are public demonstration endpoints, not an authentication system.
The demonstrated impact is disclosure and continued use of a compromised key;
do not describe it as real authentication takeover.

Contain downloads to the canonical public tree, preserve runtime configuration,
rotate the signing key to a fresh random value, and remove
`site/backups/runtime.json.bak` plus any copies of the old key under the deployed
`site/` tree. The new key must be at least 32 characters; use a CSPRNG, for example
`secrets.token_hex(32)`, rather than treating length as proof of entropy.

The trusted fixture retains the old synthetic key so the checker can test its
revocation. Baselines and local patch snapshots are teaching/evidence material;
the exercise is not a claim to erase every historical copy on the host.

The checker tests paths with encoding, double encoding and parent segments,
public files with randomized names, current-key signing, old-key rejection and
backup removal on disk. A POSIX regression test creates a symlink from public to
private and verifies containment. The request handler decodes paths once.

## 03 · Who can touch this file?

The service and checker run as your regular Linux account. State lives under
`reports/live/state/`:

| Path | Required policy |
| --- | --- |
| `private/` | Current-user owner; no group/other permissions or special bits |
| `private/service-state.json` | Current-user owner; no group/other or execute/special bits; owner must read/write |
| `exchange/` | Current-user owner; no group/other write or special bits; searchable by all for public status |
| `exchange/checkpoint.json` | Private snapshot: no group/other or execute/special bits, even after recreation |
| `exchange/status.json` | Public status: readable by all, no group/other write or execute/special bits |

Inspect the actual files with `stat`, for example:

```sh
stat -c '%a %U %G %n' reports/live/state/private/service-state.json reports/live/state/exchange/checkpoint.json
```

The vulnerable baseline assigns broad modes. The checker records this unsafe
assignment as its evidence. It **does not** demonstrate that a second account
actually opened the file: ancestor permissions, ACLs and other controls can affect
that. Do not label a mode observation as a successful cross-user exploit.

Repair `policy.json`, including creation policy (`umask`), then restart. The
service creates checkpoints by replacing the file with a newly created file, so
a one-off `chmod` does not repair future creation. The public status directory
must remain searchable; making every directory `0700` breaks this contract.

Authenticated endpoints are `GET /api/status`, `POST /api/increment`,
`POST /api/checkpoint`, and `PATCH /api/counter` with a nonnegative integer counter.
Read the synthetic service token in `fixtures/03.json`. The checker increments,
checks the new checkpoint, then restores the counter and checkpoint contents.

The checker reads kernel metadata via `lstat`, rejects symlink targets, and treats
extended POSIX ACLs as inconclusive errors rather than claiming a mode-only pass.
Missing files are errors; disabled writes are functionality failures. Use Linux
filesystem storage, not a Windows-mounted directory. No `sudo` is needed.

## Evidence

```sh
python3 check.py --challenge 01 --json reports/01-after.json
python3 tests/validate.py --output-dir reports/validation
```

Exit 0 means the requested state was observed, 1 means a contract failed, and 2
means an operational/evidence error. The fixed state requires every security and
functionality assertion to pass. Preserve report timestamps and source hashes.
Local hashes/flags are traceability aids, not signed proof or a secure scoreboard.
Record hint use and assistance; the solution guide contains spoilers.
