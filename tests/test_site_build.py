"""Behaviour tests for the hub build and the design-system vendoring check.

Run with ``python3 -m unittest discover -s tests``. Standard library only.
"""

from __future__ import annotations

import copy
import json
import re
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import build_ds_css  # noqa: E402
import build_hub  # noqa: E402


def load(name: str) -> object:
    return json.loads((ROOT / "data" / name).read_text(encoding="utf-8"))


class VendorCheck(unittest.TestCase):
    def setUp(self) -> None:
        version, tokens_text, bundle_text = build_ds_css.read_sources(None)
        self.version = version.strip()
        self.body = build_ds_css.compile_body(tokens_text, bundle_text)
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)

    def write(self, text: str, name: str | None = None) -> Path:
        path = Path(self.tmp.name) / (name or f"pin-open-{self.version}.css")
        path.write_text(text, encoding="utf-8")
        return path

    def test_fresh_copy_passes(self) -> None:
        path = self.write(build_ds_css.render(self.version, "abc1234", self.body))
        self.assertEqual(build_ds_css.check_vendor(path), self.version)

    def test_committed_vendored_file_matches_the_sources(self) -> None:
        build_ds_css.check_vendor(ROOT / "site" / "assets" / f"pin-open-{self.version}.css")

    def test_edit_without_version_bump_fails(self) -> None:
        text = build_ds_css.render(self.version, "abc1234", self.body)
        path = self.write(text.replace("--ground:#f3f3f0", "--ground:#ffffff", 1))
        with self.assertRaisesRegex(build_ds_css.DriftError, "sha256"):
            build_ds_css.check_vendor(path)

    def test_resigned_edit_still_fails_against_the_hub(self) -> None:
        edited = self.body.replace("--ground:#f3f3f0", "--ground:#ffffff", 1)
        path = self.write(build_ds_css.render(self.version, "abc1234", edited))
        with self.assertRaisesRegex(build_ds_css.DriftError, "differs"):
            build_ds_css.check_vendor(path)

    def test_other_version_fails(self) -> None:
        path = self.write(build_ds_css.render("9.9.9", "abc1234", self.body), "pin-open-9.9.9.css")
        with self.assertRaisesRegex(build_ds_css.DriftError, "version"):
            build_ds_css.check_vendor(path)

    def test_missing_header_fails(self) -> None:
        with self.assertRaisesRegex(build_ds_css.DriftError, "header"):
            build_ds_css.check_vendor(self.write(self.body))

    def test_dark_theme_switches_exist_for_media_query_and_attribute(self) -> None:
        dark_blocks = re.findall(r'(?:prefers-color-scheme: dark\)\{:root:not\(\[data-theme="light"\]\)|:root\[data-theme="dark"\])\{([^}]*)\}', self.body)
        self.assertEqual(len(dark_blocks), 2)
        for block in dark_blocks:
            self.assertIn("--art-line-filter:brightness(1.65)", block)
            self.assertIn("--haze-mult:0.8", block)
            self.assertIn("--rust:#f2a07a", block)


class HubBuild(unittest.TestCase):
    def setUp(self) -> None:
        self.projects = load("projects.json")
        self.config = load("featured.json")
        self.by_name = build_hub.project_index(self.projects)

    def test_agentcenter_card_states_agpl_and_never_mit(self) -> None:
        page = build_hub.build_index(self.config, self.by_name)
        card = re.search(r'<article[^>]*aria-labelledby="card-agentcenter".*?</article>', page, re.S).group(0)
        self.assertIn("AGPL-3.0-or-later", card)
        self.assertNotIn("MIT", page)

    def test_stale_licence_snapshot_is_refused(self) -> None:
        projects = copy.deepcopy(self.projects)
        for project in projects:
            if project["name"] == "agentcenter":
                project["license_api"] = "MIT | LICENSE"
        with self.assertRaisesRegex(ValueError, "agentcenter.*MIT"):
            build_hub.check_featured_licenses(self.config, build_hub.project_index(projects))

    def test_unknown_hue_is_refused(self) -> None:
        config = copy.deepcopy(self.config)
        config["featured"][0]["hue"] = "purple"
        with self.assertRaisesRegex(ValueError, "hue"):
            build_hub.check_featured_licenses(config, self.by_name)

    def test_json_ld_parses_and_mirrors_the_featured_pages(self) -> None:
        page = build_hub.build_index(self.config, self.by_name)
        blocks = re.findall(r'<script type="application/ld\+json">(.*?)</script>', page, re.S)
        self.assertEqual(len(blocks), 1)
        data = json.loads(blocks[0])
        self.assertEqual(data["@type"], "ProfilePage")
        self.assertEqual([part["url"] for part in data["hasPart"]], [item["page_url"] for item in self.config["featured"]])

    def test_head_limits(self) -> None:
        self.assertLessEqual(len(build_hub.TITLE), 60)
        self.assertLessEqual(len(build_hub.DESCRIPTION), 155)
        page = build_hub.build_index(self.config, self.by_name)
        self.assertEqual(page.count("<h1"), 1)
        self.assertIn(f'<link rel="canonical" href="{build_hub.SITE_URL}">', page)

    def test_not_found_page_uses_root_absolute_assets_and_noindex(self) -> None:
        page = build_hub.build_404(self.config)
        self.assertIn('<meta name="robots" content="noindex">', page)
        for ref in re.findall(r'(?:href|src)="([^"#]+)"', page):
            self.assertTrue(ref.startswith(("/eduardopin/", "https://")), ref)

    def test_sitemap_lists_only_the_canonical(self) -> None:
        sitemap = build_hub.build_sitemap(self.config)
        self.assertEqual(re.findall(r"<loc>(.*?)</loc>", sitemap), [build_hub.SITE_URL])


if __name__ == "__main__":
    unittest.main()
