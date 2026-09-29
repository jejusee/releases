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
        "assets": {"any": {"url": "https://example.invalid/a", "sha256": "0" * 64}},
    }


class VersionTests(unittest.TestCase):
    def m(self, stable=None, pre=None, versions=None, label="dev", strategy="semver"):
        return {
            "schema": 2,
            "project": "x",
            "versioning": {"strategy": strategy, "prerelease": label},
            "stable": stable,
            "prerelease": pre,
            "versions": versions or {},
        }

    def test_first_release_requires_explicit_direction(self):
        with self.assertRaises(SystemExit):
            hub.next_version(self.m(), "dev", "auto")
        self.assertEqual(hub.next_version(self.m(), "dev", "minor"), "0.1.0-dev.1")
        self.assertEqual(hub.next_version(self.m(), "dev", "custom", "0.5.0"), "0.5.0-dev.1")

    def test_auto_starts_patch_after_stable(self):
        self.assertEqual(hub.next_version(self.m(entry("1.2.3")), "dev", "auto"), "1.2.4-dev.1")

    def test_auto_continues_active_line(self):
        versions = {"1.3.0-dev.1": entry("1.3.0-dev.1"), "1.3.0-dev.2": entry("1.3.0-dev.2")}
        m = self.m(entry("1.2.3"), entry("1.3.0-dev.2"), versions)
        self.assertEqual(hub.next_version(m, "dev", "auto"), "1.3.0-dev.3")

    def test_bumps_are_based_on_stable(self):
        m = self.m(entry("1.2.3"), entry("1.2.4-dev.5"), {"1.2.4-dev.5": entry("1.2.4-dev.5")})
        self.assertEqual(hub.next_version(m, "dev", "patch"), "1.2.4-dev.6")
        self.assertEqual(hub.next_version(m, "dev", "minor"), "1.3.0-dev.1")
        self.assertEqual(hub.next_version(m, "dev", "major"), "2.0.0-dev.1")

    def test_custom_can_skip_version(self):
        m = self.m(entry("0.0.9"), entry("0.1.0-dev.5"), {"0.1.0-dev.5": entry("0.1.0-dev.5")})
        self.assertEqual(hub.next_version(m, "dev", "custom", "0.1.3"), "0.1.3-dev.1")

    def test_cannot_move_backward(self):
        m = self.m(entry("0.1.0"), entry("0.3.0-dev.1"), {"0.3.0-dev.1": entry("0.3.0-dev.1")})
        with self.assertRaises(SystemExit):
            hub.next_version(m, "dev", "custom", "0.2.0")

    def test_stable_promotes_active_prerelease(self):
        m = self.m(entry("1.2.3"), entry("1.3.0-dev.4"))
        self.assertEqual(hub.next_version(m, "release-stable"), "1.3.0")

    def test_configurable_prerelease_label(self):
        m = self.m(entry("1.0.0"), label="rc")
        self.assertEqual(hub.next_version(m, "dev", "minor"), "1.1.0-rc.1")

    def test_legacy_contract_remains_available(self):
        self.assertEqual(hub.next_version(self.m(entry("1.2.3")), "dev-minor"), "1.3.0-rc.1")
        self.assertEqual(hub.next_version(self.m(entry("1.2.3"), entry("1.3.0-rc.4")), "dev-rc"), "1.3.0-rc.5")

    def test_custom_strategy_accepts_project_version(self):
        m = self.m(strategy="custom")
        self.assertEqual(hub.next_version(m, "dev", target="2026.09-build.3"), "2026.09-build.3")


if __name__ == "__main__":
    unittest.main()
