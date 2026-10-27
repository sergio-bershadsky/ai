"""Run: python3 -m unittest discover -s plugins/epic-observation/skills/epic-observation/tests"""

import copy
import json
import sys
import unittest
from pathlib import Path

SKILL = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SKILL / "scripts"))
import observe  # noqa: E402  # pyright: ignore[reportMissingImports]

SEED = json.loads((SKILL / "assets" / "sample-seed.json").read_text())
PROFILES = sorted((SKILL / "assets" / "profiles").glob("*.json"))


class MergeConfig(unittest.TestCase):
    def test_epic_config_wins_and_nested_maps_merge(self):
        profile = {"tracker": {"name": "Jira"}, "people": {"ana": {"name": "Ana"}}, "statusMap": {"item": {}}}
        out = observe.merge_config(profile, {"title": "T", "people": {"bo": {"name": "Bo"}}})
        self.assertEqual(out["title"], "T")
        self.assertEqual(set(out["people"]), {"ana", "bo"})
        self.assertNotIn("statusMap", out, "tooling-only keys must not reach the page")


class ResolveStatus(unittest.TestCase):
    MAP = {"item": {"To Do": "ready", "Code Review": "in_review"}}

    def test_mapped_label_is_case_insensitive(self):
        self.assertEqual(observe.resolve_status("item", "code review", self.MAP), "in_review")

    def test_canonical_label_passes_through(self):
        self.assertEqual(observe.resolve_status("item", "In Progress", self.MAP), "in_progress")

    def test_unmapped_label_is_refused(self):
        with self.assertRaises(observe.UnmappedStatus):
            observe.resolve_status("item", "QA", self.MAP)

    def test_normalize_reports_every_unmapped_label_and_keeps_mapped_ones(self):
        seed = {"events": [{"at": "2026-09-07T09:00:00Z", "effects": [
            {"type": "item", "id": "A-1", "label": "Code Review"},
            {"type": "item", "id": "A-2", "label": "QA"},
            {"type": "change", "id": "#1", "label": "Shipped"}]}]}
        problems = observe.normalize(seed, {"statusMap": self.MAP})
        self.assertEqual(seed["events"][0]["effects"][0]["status"], "in_review")
        self.assertEqual(len(problems), 2)
        self.assertNotIn("status", seed["events"][0]["effects"][1])


class Validate(unittest.TestCase):
    def test_sample_seed_is_clean(self):
        self.assertEqual(observe.validate(SEED), [])

    def test_catches_unknown_blocker_noncanonical_status_and_local_time(self):
        seed = copy.deepcopy(SEED)
        seed["items"]["SHOP-104"]["blockedBy"].append("SHOP-999")
        seed["events"][0]["at"] = "2026-09-07 09:00"
        seed["events"][1]["effects"][0]["status"] = "To Do"
        problems = "\n".join(observe.validate(seed))
        self.assertIn("SHOP-999", problems)
        self.assertIn("ISO-8601", problems)
        self.assertIn("not canonical", problems)


class Profiles(unittest.TestCase):
    def test_every_example_profile_maps_only_to_canonical_statuses(self):
        self.assertTrue(PROFILES)
        for path in PROFILES:
            profile = json.loads(path.read_text())
            self.assertIn("name", profile.get("tracker", {}), path.name)
            for kind, table in profile.get("statusMap", {}).items():
                bad = set(table.values()) - observe.CANONICAL[kind]
                self.assertFalse(bad, f"{path.name} {kind}: {bad}")


class Export(unittest.TestCase):
    def test_seed_is_embedded_and_script_close_is_escaped(self):
        seed = copy.deepcopy(SEED)
        seed["events"][0]["detail"] = "evil </script><script>alert(1)"
        page = observe.export(seed, {"tracker": {"name": "Jira"}})
        self.assertTrue(page.startswith("<!doctype html>\n<meta charset=\"utf-8\">"))
        start = page.index('<script type="application/json" id="seed">')
        self.assertLess(start, page.index("<script>\n"))
        self.assertNotIn("</script><script>alert", page)
        payload = page[start:].split(">", 1)[1].split("</script>", 1)[0]
        self.assertEqual(json.loads(payload.replace("<\\/", "</"))["config"]["tracker"]["name"], "Jira")


if __name__ == "__main__":
    unittest.main()
