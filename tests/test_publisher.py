"""Additive publication preflight and repeat-run protection."""

import json
import tempfile
import unittest
from pathlib import Path
from sys import path as sys_path

sys_path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from publish_to_cybermancy import publish


class PublisherTest(unittest.TestCase):
    def test_dry_run_write_then_refuse_overwrite(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            repo = root / "cybermancy"
            family = repo / "src/packs/adventures/adversaries"
            family.mkdir(parents=True)
            (repo / "src/packs/adventures/environments").mkdir()
            (repo / "module.json").write_text("{}")
            (family / "Tier_2_FOLDER1234567890.json").write_text(json.dumps({"name": "Tier 2"}))
            pkg = root / "test-package"
            for rel in ("source", "foundry", "print", "assets/images/adversaries", "assets/tokens/adversaries"):
                (pkg / rel).mkdir(parents=True)
            slug = "test-hunter"
            (pkg / "validation.json").write_text(json.dumps({"slug": slug, "status": "pass", "gates": [{"status": "pass"}]}))
            spec = {"entityType": "adversary", "identity": {"slug": slug, "name": "Test Hunter", "tier": 2},
                    "provenance": {"status": "approved"}, "art": {
                        "portrait": {"path": f"modules/cybermancy/assets/images/adversaries/{slug}.png"},
                        "token": {"path": f"modules/cybermancy/assets/tokens/adversaries/{slug}-token.png"}}}
            (pkg / "source" / f"{slug}.spec.json").write_text(json.dumps(spec))
            actor = {"name": "Test Hunter", "type": "adversary", "_id": "TestActor1234567", "folder": "FOLDER1234567890",
                     "items": [], "_key": "!actors!TestActor1234567"}
            (pkg / "foundry" / f"{slug}.json").write_text(json.dumps(actor))
            (pkg / "print" / f"{slug}.pdf").write_bytes(b"pdf")
            for name in (f"assets/images/adversaries/{slug}.png", f"assets/tokens/adversaries/{slug}-token.png"):
                (pkg / name).write_bytes(b"image")
            self.assertEqual(len(publish([pkg], repo)), 5)
            self.assertFalse((family / "Test_Hunter_TestActor1234567.json").exists())
            publish([pkg], repo, write=True)
            self.assertTrue((family / "Test_Hunter_TestActor1234567.json").exists())
            with self.assertRaisesRegex(ValueError, "already exists"):
                publish([pkg], repo, write=True)


if __name__ == "__main__":
    unittest.main()
