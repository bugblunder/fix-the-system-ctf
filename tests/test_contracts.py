"""Real native HTTP and filesystem checks, including deliberately inadequate repairs."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from lab.fixtures import generate
from grader.checks import metadata
from support import ROOT, make_project, running


class Contracts(unittest.TestCase):
    def grade(self, key, fixed=False, edit=None, seed=1):
        with running(key, fixed, edit, seed) as case:
            report = case.report()
        self.assertFalse(report["errors"], report["errors"])
        return report

    def test_all_vulnerable_baselines(self):
        for key in ("01", "02", "03"):
            with self.subTest(challenge=key):
                report = self.grade(key)
                self.assertTrue(report["baseline_reproduced"], report)
                self.assertTrue(report["functionality_pass"], report)
                self.assertFalse(report["technical_pass"])

    def test_all_references_preserve_behavior(self):
        for key in ("01", "02", "03"):
            with self.subTest(challenge=key):
                report = self.grade(key, True)
                self.assertTrue(report["technical_pass"], report)
                self.assertFalse(any(report["baseline_witnesses"].values()))

    def test_reference_over_multiple_randomized_shapes(self):
        for seed in (7, 19, 43):
            for key in ("01", "02"):
                with self.subTest(seed=seed, challenge=key):
                    self.assertTrue(self.grade(key, True, seed=seed)["technical_pass"])

    def test_deny_all_and_admin_only_fail_functionality(self):
        for decision in ("False", "actor['role'] == 'admin'"):
            def edit(work):
                with (work / "policy.py").open("a") as output:
                    output.write(f'\ndef can_access(actor, invoice, operation="read"):\n    return {decision}\n')
            with self.subTest(decision=decision):
                report = self.grade("01", True, edit)
                self.assertFalse(report["functionality_pass"])
                self.assertIsNone(report["technical_flag"])

    def test_known_id_allowlist_does_not_win(self):
        def edit(work):
            with (work / "policy.py").open("a") as output:
                output.write('\ndef can_access(actor, invoice, operation="read"):\n    return invoice["id"] in {"101", "102", "103", "104"}\n')
        self.assertFalse(self.grade("01", True, edit)["technical_pass"])

    def test_correct_policy_with_indirect_bypass_fails(self):
        def edit(work):
            shutil.copy2(ROOT / "baselines/01-authorization/app.py", work / "app.py")
        self.assertFalse(self.grade("01", True, edit)["security_pass"])

    def test_object_check_without_field_allowlist_fails(self):
        def edit(work):
            with (work / "policy.py").open("a") as out:
                out.write('\ndef apply_patch(invoice, body):\n    invoice.update(body)\n    return True\n')
        self.assertFalse(self.grade("01", True, edit)["security_pass"])

    def test_disabling_updates_fails_functionality(self):
        def edit(work):
            path = work / "policy.py"
            with path.open("a") as stream:
                stream.write('\ndef apply_patch(invoice, body):\n    return False\n')
        self.assertFalse(self.grade("01", True, edit)["functionality_pass"])

    def test_partial_note_mutation_before_rejection_fails(self):
        def edit(work):
            path = work / "policy.py"
            path.write_text(path.read_text().replace('def apply_patch(invoice, body):',
                'def apply_patch(invoice, body):\n    if "note" in body:\n        invoice["note"] = body["note"]'))
        self.assertFalse(self.grade("01", True, edit)["security_pass"])

    def test_manager_write_privileges_fail(self):
        def edit(work):
            path = work / "policy.py"
            path.write_text(path.read_text().replace('operation == "read" and actor["team"]', 'actor["team"]'))
        self.assertFalse(self.grade("01", True, edit)["security_pass"])

    def test_missing_denial_logging_fails_checker(self):
        def edit(work):
            path = work / "app.py"
            path.write_text(path.read_text().replace('self.event("authorization_denied", actor, key)', 'pass'))
        report = self.grade("01", True, edit)
        self.assertFalse(report["security_pass"])
        self.assertTrue(report["functionality_pass"])

    def test_checker_restores_invoices(self):
        for fixed in (False, True):
            with running("01", fixed) as case:
                before = case.client.request("/api/invoices", "admin").json()
                self.assertFalse(case.report()["errors"])
                self.assertEqual(case.client.request("/api/invoices", "admin").json(), before)

    def test_block_all_downloads_breaks_feature(self):
        def edit(work):
            (work / "policy.py").write_text('def resolve_public(site, name):\n    return None\n')
        report = self.grade("02", True, edit)
        self.assertTrue(report["security_pass"])
        self.assertFalse(report["functionality_pass"])

    def test_backup_only_blocklist_fails(self):
        def edit(work):
            source = (ROOT / "baselines/02-exposure/policy.py").read_text()
            source = source.replace('target = (site / name).resolve()', 'if name.endswith(".bak"):\n        return None\n    target = (site / name).resolve()')
            (work / "policy.py").write_text(source)
        self.assertFalse(self.grade("02", True, edit)["security_pass"])

    def test_containment_alone_does_not_remediate_compromise(self):
        def edit(work):
            shutil.copy2(ROOT / "solutions/02-exposure/policy.py", work / "policy.py")
        report = self.grade("02", edit=edit)
        self.assertTrue(report["functionality_pass"])
        self.assertFalse(report["security_pass"])
        failures = {x["name"] for x in report["checks"] if not x["passed"]}
        self.assertTrue({"key_rotated", "backup_removed", "old_key_revoked"} <= failures)

    def test_rotation_without_removing_backup_fails(self):
        def edit(work):
            fixture = json.loads((work.parents[1] / "fixtures/02.json").read_text())
            backup = work / "site/backups/runtime.json.bak"
            backup.parent.mkdir()
            backup.write_text(fixture["compromised_key"])
        self.assertFalse(self.grade("02", True, edit)["security_pass"])

    def test_deleted_config_breaks_functionality(self):
        report = self.grade("02", True, lambda work: (work / "site/private/runtime.json").unlink())
        self.assertFalse(report["functionality_pass"])

    def test_symlink_containment_and_double_encoding(self):
        def edit(work):
            (work / "site/public/leak.json").symlink_to("../private/runtime.json")
        self.assertTrue(self.grade("02", True, edit)["technical_pass"])
        with running("02", edit=edit) as case:
            self.assertEqual(case.client.request("/files/public/leak.json").status, 200)

    def test_catalog_reloads_real_config(self):
        with running("02", True) as case:
            path = case.work / "site/private/runtime.json"
            config = json.loads(path.read_text())
            config["store"] = "New runtime setting"
            path.write_text(json.dumps(config))
            self.assertEqual(case.client.request("/api/catalog").json()["store"], "New runtime setting")

    def test_group_write_and_unsafe_creation_fail(self):
        for field, value in (("file_mode", "0660"), ("directory_mode", "0770"),
                             ("exchange_mode", "0775"), ("umask", "0007")):
            def edit(work):
                path = work / "policy.json"
                data = json.loads(path.read_text())
                data[field] = value
                path.write_text(json.dumps(data))
            with self.subTest(field=field):
                report = self.grade("03", True, edit)
                self.assertTrue(report["functionality_pass"], report)
                self.assertFalse(report["security_pass"])

    def test_read_only_state_breaks_increment(self):
        def edit(work):
            path = work / "policy.json"
            data = json.loads(path.read_text())
            data["file_mode"] = "0400"
            path.write_text(json.dumps(data))
        report = self.grade("03", True, edit)
        self.assertFalse(report["functionality_pass"])

    def test_private_exchange_breaks_public_contract(self):
        def edit(work):
            path = work / "policy.json"
            data = json.loads(path.read_text())
            data["exchange_mode"] = "0700"
            path.write_text(json.dumps(data))
        self.assertFalse(self.grade("03", True, edit)["functionality_pass"])

    def test_missing_state_is_error_not_secure(self):
        with running("03", True) as case:
            (case.state / "private/service-state.json").unlink()
            report = case.report()
        self.assertTrue(report["errors"])
        self.assertFalse(report["technical_pass"])

    def test_checker_restores_counter(self):
        with running("03", True) as case:
            before = (case.state / "private/service-state.json").read_bytes()
            self.assertTrue(case.report()["technical_pass"])
            self.assertEqual((case.state / "private/service-state.json").read_bytes(), before)

    def test_permission_metadata_refuses_symlinks(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "target"
            path.write_text("synthetic")
            link = Path(directory) / "link"
            link.symlink_to(path)
            with self.assertRaises(RuntimeError):
                metadata(link)

    def test_reset_randomizes_and_snapshots_scoped_work(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "project"
            make_project(root)
            before = (root / "fixtures/01.json").read_bytes()
            policy = root / "challenges/01-authorization/policy.py"
            policy.write_text("# participant change\n")
            unrelated = root / "challenges/02-exposure/policy.py"
            unrelated.write_text("# keep me\n")
            command = [sys.executable, "manage.py", "reset", "--challenge", "01"]
            refused = subprocess.run(command, cwd=root, capture_output=True)
            self.assertEqual(refused.returncode, 2)
            self.assertEqual(policy.read_text(), "# participant change\n")
            accepted = subprocess.run(command + ["--yes"], cwd=root, capture_output=True)
            self.assertEqual(accepted.returncode, 0, accepted.stderr)
            self.assertNotEqual((root / "fixtures/01.json").read_bytes(), before)
            self.assertEqual(unrelated.read_text(), "# keep me\n")
            snapshots = list((root / "reports/patch-backups").glob("*/01-authorization"))
            self.assertEqual(len(snapshots), 1)
            self.assertEqual((snapshots[0] / "policy.py").read_text(), "# participant change\n")
            self.assertEqual((snapshots[0] / "fixture-before.json").read_bytes(), before)

    def test_fixture_generation_changes_ids_and_credentials(self):
        first, second = generate("01"), generate("01")
        self.assertNotEqual(first["actors"]["alice"]["token"], second["actors"]["alice"]["token"])
        self.assertFalse({x["id"] for x in first["invoices"]} & {x["id"] for x in second["invoices"]})


if __name__ == "__main__":
    unittest.main()
