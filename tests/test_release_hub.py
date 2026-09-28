import importlib.util
import pathlib
import unittest

MODULE = pathlib.Path(__file__).parents[1] / "scripts" / "release_hub.py"
spec = importlib.util.spec_from_file_location("release_hub", MODULE)
hub = importlib.util.module_from_spec(spec)
spec.loader.exec_module(hub)

def entry(version):
    return {
        "version": version,
        "published_at": "2026-01-01T00:00:00Z",
        "assets": {"any": {"url": "https://example.invalid/a", "sha256": "0"*64}},
    }

class VersionTests(unittest.TestCase):
    def m(self, stable=None, pre=None):
        return {"schema":2, "project":"x", "stable": stable, "prerelease": pre, "versions":{}}

    def test_first_patch(self):
        self.assertEqual(hub.next_version(self.m(), "dev-patch"), "0.0.1-rc.1")

    def test_first_minor(self):
        self.assertEqual(hub.next_version(self.m(), "dev-minor"), "0.1.0-rc.1")

    def test_first_major(self):
        self.assertEqual(hub.next_version(self.m(), "dev-major"), "1.0.0-rc.1")

    def test_bumps(self):
        m = self.m(entry("1.2.3"))
        self.assertEqual(hub.next_version(m, "dev-patch"), "1.2.4-rc.1")
        self.assertEqual(hub.next_version(m, "dev-minor"), "1.3.0-rc.1")
        self.assertEqual(hub.next_version(m, "dev-major"), "2.0.0-rc.1")

    def test_dev_rc(self):
        self.assertEqual(
            hub.next_version(self.m(entry("1.2.3"), entry("1.3.0-rc.4")), "dev-rc"),
            "1.3.0-rc.5",
        )

    def test_release_stable(self):
        self.assertEqual(
            hub.next_version(self.m(entry("1.2.3"), entry("1.3.0-rc.4")), "release-stable"),
            "1.3.0",
        )

    def test_no_new_cycle_while_rc_active(self):
        with self.assertRaises(SystemExit):
            hub.next_version(self.m(entry("1.2.3"), entry("1.3.0-rc.1")), "dev-minor")

if __name__ == "__main__":
    unittest.main()
