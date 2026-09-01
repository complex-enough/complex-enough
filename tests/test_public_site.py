from __future__ import annotations

import re
import unittest
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit


ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"
PAGES_WORKFLOW = ROOT / ".github" / "workflows" / "pages.yml"


class LinkParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.links: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)
        attribute = "href" if tag in {"a", "link"} else "src" if tag in {"img", "script"} else None
        if attribute and values.get(attribute):
            self.links.append(values[attribute] or "")


class PublicSiteTest(unittest.TestCase):
    def test_pages_publish_is_release_tag_driven_with_manual_recovery(self) -> None:
        workflow = PAGES_WORKFLOW.read_text(encoding="utf-8")
        self.assertIn('tags:\n      - "v*"', workflow)
        self.assertIn("workflow_dispatch:", workflow)
        self.assertIn("packaging/plugin.json", workflow)
        self.assertIn("$GITHUB_REF_NAME", workflow)

    def test_all_relative_html_and_asset_links_resolve(self) -> None:
        for page in sorted(SITE.rglob("*.html")):
            with self.subTest(page=page.relative_to(SITE)):
                parser = LinkParser()
                parser.feed(page.read_text(encoding="utf-8"))
                for link in parser.links:
                    parsed = urlsplit(link)
                    if parsed.scheme or parsed.netloc or link.startswith(("mailto:", "#")):
                        continue
                    target = (page.parent / parsed.path).resolve()
                    if parsed.path.endswith("/") or not target.suffix:
                        target /= "index.html"
                    self.assertTrue(
                        target.is_file(),
                        f"{page.relative_to(SITE)} has missing local target {link}",
                    )

    def test_site_is_static_and_tracking_free(self) -> None:
        forbidden = re.compile(
            r"google-analytics|googletagmanager|segment\.io|facebook\.net|<script\s+[^>]*src=",
            re.IGNORECASE,
        )
        for page in sorted(SITE.rglob("*.html")):
            with self.subTest(page=page.relative_to(SITE)):
                content = page.read_text(encoding="utf-8")
                self.assertNotRegex(content, forbidden)
                self.assertNotIn("http://", content)

    def test_bilingual_public_identity_and_policy_urls_are_consistent(self) -> None:
        for relative in (
            "en/privacy/index.html",
            "en/terms/index.html",
            "en/support/index.html",
            "zh-TW/privacy/index.html",
            "zh-TW/terms/index.html",
            "zh-TW/support/index.html",
        ):
            content = (SITE / relative).read_text(encoding="utf-8")
            self.assertIn("Huan Min Wei", content)
            self.assertIn("support@complexenough.com", content)
        sitemap = (SITE / "sitemap.xml").read_text(encoding="utf-8")
        self.assertEqual(sitemap.count("<url>"), 10)
        self.assertNotIn("dryada" + "70749", sitemap)


if __name__ == "__main__":
    unittest.main()
