#!/usr/bin/env python3
"""Build the portfolio hub and the generated profile README project table.

Project facts live in ``data/projects.json`` and the small editorial layer lives
in ``data/featured.json``. When a project page goes live, edit its ``page_url``
and related status in ``data/featured.json``, then run ``python3
scripts/build_hub.py``. The script uses only the Python standard library and
writes ``site/index.html``, ``site/404.html``, ``site/sitemap.xml`` plus the content between the project markers in
``README.md`` deterministically.
"""

from __future__ import annotations

import html
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROJECTS_PATH = ROOT / "data" / "projects.json"
FEATURED_PATH = ROOT / "data" / "featured.json"
INDEX_PATH = ROOT / "site" / "index.html"
NOT_FOUND_PATH = ROOT / "site" / "404.html"
SITEMAP_PATH = ROOT / "site" / "sitemap.xml"
README_PATH = ROOT / "README.md"
PROJECTS_START = "<!-- projects:start -->"
PROJECTS_END = "<!-- projects:end -->"
PROFILE_NAME = "eduardopin"


def load_json(path: Path) -> object:
    with path.open(encoding="utf-8") as source:
        return json.load(source)


def escape(value: object) -> str:
    return html.escape(str(value), quote=True)


def markdown_cell(value: object) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ")


def project_index(projects: list[dict[str, object]]) -> dict[str, dict[str, object]]:
    indexed = {str(project["name"]): project for project in projects}
    if len(indexed) != len(projects):
        raise ValueError("Project names must be unique")
    return indexed


def configured_names(config: dict[str, object]) -> list[str]:
    names = [str(item["name"]) for item in config["featured"]]
    for group in config["reference_groups"]:
        names.extend(str(name) for name in group["projects"])
    names.extend(str(item["name"]) for item in config["older"])
    return names


def validate(
    projects: list[dict[str, object]],
    config: dict[str, object],
    by_name: dict[str, dict[str, object]],
) -> None:
    if PROFILE_NAME not in by_name:
        raise ValueError(f"Missing profile repository: {PROFILE_NAME}")

    names = configured_names(config)
    if len(names) != len(set(names)):
        raise ValueError("Each project must appear in exactly one configured group")

    expected = set(by_name) - {PROFILE_NAME}
    actual = set(names)
    if actual != expected:
        missing = sorted(expected - actual)
        extra = sorted(actual - expected)
        raise ValueError(f"Project grouping mismatch; missing={missing}, extra={extra}")

    for project in projects:
        name = str(project["name"])
        expected_url = f"https://github.com/eduardopin/{name}"
        if project["url"] != expected_url:
            raise ValueError(f"Unexpected repository URL for {name}")


SITE_URL = "https://eduardopin.github.io/eduardopin/"
BASE_PATH = "/eduardopin/"
TITLE = "Eduardo Pin — Cloud, platform, SRE, FinOps and DevSecOps"
DESCRIPTION = (
    "Cloud, platform engineering, SRE, FinOps and DevSecOps work by Eduardo Pin: "
    "three open-source tools and public-safe reference examples."
)
OG_ALT = "Eduardo Pin: AgenFK Squad, AgentCenter and AWS IaC Enterprise Library"
FONTS_URL = (
    "https://fonts.googleapis.com/css2?family=Archivo:wdth,wght@62..125,100..900"
    "&family=Martian+Mono:wdth,wght@75..112.5,100..800&display=swap"
)
HUE_CLASSES = {"rust", "green", "amber", "violet"}
UNCLAIMED_LICENSES = {"", "none", "NOASSERTION"}

GITHUB_ICON = (
    '<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path fill="currentColor" d="M12 2a10 10 0 0 0-3.16 '
    "19.49c.5.09.68-.22.68-.48v-1.7c-2.78.6-3.37-1.34-3.37-1.34-.45-1.16-1.11-1.47-1.11-1.47-.91-.62.07-.6.07-.6 1 .07 "
    "1.53 1.03 1.53 1.03.9 1.52 2.34 1.08 2.91.83.09-.65.35-1.09.63-1.34-2.22-.25-4.55-1.11-4.55-4.94 0-1.09.39-1.98 "
    "1.03-2.68-.1-.25-.45-1.27.1-2.64 0 0 .84-.27 2.75 1.02a9.5 9.5 0 0 1 5 0c1.91-1.29 2.75-1.02 2.75-1.02.55 1.37.2 "
    "2.39.1 2.64.64.7 1.03 1.59 1.03 2.68 0 3.84-2.34 4.68-4.57 4.93.36.31.68.92.68 1.85v2.74c0 .27.18.58.69.48A10 10 "
    '0 0 0 12 2z"/></svg>'
)
STAR_ICON = (
    '<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path d="M12 2.8l2.8 5.7 6.3.9-4.6 4.4 1.1 6.2L12 '
    '17.1 6.4 20l1.1-6.2L2.9 9.4l6.3-.9z" fill="none" stroke="currentColor" stroke-width="1.6" '
    'stroke-linejoin="round"/></svg>'
)
TRACE_SVG = (
    '<svg viewBox="0 0 1200 600" preserveAspectRatio="xMidYMid slice" aria-hidden="true" focusable="false"><defs>'
    '<path id="tr-p0" d="M-20 150 H520 L580 210 H1220" pathLength="100"/>'
    '<path id="tr-p1" d="M-20 330 H380 L460 410 H820 L860 370 H1220" pathLength="100"/>'
    '<path id="tr-p2" d="M-20 500 H640 L700 440 H1220" pathLength="100"/>'
    '<linearGradient id="tr-band" gradientUnits="userSpaceOnUse" x1="0" x2="1200">'
    '<stop offset="0" stop-color="currentColor" stop-opacity="0"/><stop offset=".5" stop-color="currentColor" '
    'stop-opacity=".1"/><stop offset="1" stop-color="currentColor" stop-opacity="0"/></linearGradient>'
    '<linearGradient id="tr-line" gradientUnits="userSpaceOnUse" x1="0" x2="1200">'
    '<stop offset="0" stop-color="currentColor" stop-opacity=".12"/><stop offset=".25" stop-color="currentColor" '
    'stop-opacity=".5"/><stop offset=".5" stop-color="currentColor" stop-opacity=".19"/><stop offset=".75" '
    'stop-color="currentColor" stop-opacity=".33"/><stop offset="1" stop-color="currentColor" stop-opacity=".09"/>'
    "</linearGradient></defs>"
    + "".join(f'<use href="#tr-p{i}" class="band" stroke="url(#tr-band)"/>' for i in range(3))
    + "".join(f'<use href="#tr-p{i}" class="line" stroke="url(#tr-line)"/>' for i in range(3))
    + "".join(f'<use href="#tr-p{i}" class="trail trail-{i + 1}"/>' for i in range(3))
    + "</svg>"
)


def ds_version() -> str:
    return (ROOT / "design-system" / "VERSION").read_text(encoding="utf-8").strip()


def check_featured_licenses(config: dict[str, object], by_name: dict[str, dict[str, object]]) -> None:
    """A licence the GitHub snapshot reports must appear in the card's licence note.

    The page prints only ``license_note``; this stops a stale ``license_api`` in
    ``data/projects.json`` (it once said MIT for AgentCenter) from sitting unnoticed
    next to a note that says something else.
    """
    for item in config["featured"]:
        if str(item.get("hue")) not in HUE_CLASSES:
            raise ValueError(f"{item['name']}: hue must be one of {sorted(HUE_CLASSES)}")
        project = by_name[str(item["name"])]
        spdx = str(project.get("license_api") or "").split("|")[0].strip()
        if spdx in UNCLAIMED_LICENSES:
            continue
        if spdx not in str(item["license_note"]):
            raise ValueError(
                f"{item['name']}: data/projects.json reports {spdx}, but the licence note says "
                f"{item['license_note']!r}; refresh the snapshot or fix the note"
            )


def head(title: str, description: str, *, asset_base: str, canonical: str | None, noindex: bool) -> str:
    version = ds_version()
    lines = [
        '<meta charset="utf-8">',
        '<meta name="viewport" content="width=device-width, initial-scale=1">',
        f"<title>{escape(title)}</title>",
        f'<meta name="description" content="{escape(description)}">',
    ]
    if noindex:
        lines.append('<meta name="robots" content="noindex">')
    if canonical:
        lines.append(f'<link rel="canonical" href="{canonical}">')
    lines += [
        '<meta name="theme-color" content="#f3f3f0" media="(prefers-color-scheme: light)">',
        '<meta name="theme-color" content="#101214" media="(prefers-color-scheme: dark)">',
        f'<link rel="icon" href="{asset_base}favicon.svg" type="image/svg+xml">',
    ]
    if canonical:
        lines += [
            '<meta property="og:type" content="website">',
            '<meta property="og:site_name" content="Eduardo Pin">',
            '<meta property="og:locale" content="en_US">',
            f'<meta property="og:title" content="{escape(title)}">',
            f'<meta property="og:description" content="{escape(description)}">',
            f'<meta property="og:url" content="{canonical}">',
            f'<meta property="og:image" content="{SITE_URL}og.png">',
            '<meta property="og:image:width" content="1200">',
            '<meta property="og:image:height" content="630">',
            f'<meta property="og:image:alt" content="{escape(OG_ALT)}">',
            '<meta name="twitter:card" content="summary_large_image">',
            f'<meta name="twitter:title" content="{escape(title)}">',
            f'<meta name="twitter:description" content="{escape(description)}">',
            f'<meta name="twitter:image" content="{SITE_URL}og.png">',
            f'<meta name="twitter:image:alt" content="{escape(OG_ALT)}">',
        ]
    lines += [
        '<link rel="preconnect" href="https://fonts.googleapis.com">',
        '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>',
        f'<link rel="stylesheet" href="{escape(FONTS_URL)}">',
        f'<link rel="stylesheet" href="{asset_base}assets/pin-open-{version}.css">',
        f'<link rel="stylesheet" href="{asset_base}styles.css">',
    ]
    return "\n".join(f"  {line}" for line in lines)


def json_ld(config: dict[str, object]) -> str:
    data = {
        "@context": "https://schema.org",
        "@type": "ProfilePage",
        "url": SITE_URL,
        "name": TITLE,
        "inLanguage": "en",
        "mainEntity": {
            "@type": "Person",
            "@id": f"{SITE_URL}#person",
            "name": "Eduardo Pin",
            "url": SITE_URL,
            "sameAs": ["https://github.com/eduardopin"],
            "knowsAbout": [
                "Cloud infrastructure",
                "Platform engineering",
                "Site reliability engineering",
                "FinOps",
                "DevSecOps",
                "Terraform",
                "AWS",
            ],
        },
        "hasPart": [
            {"@type": item["schema_type"], "name": item["schema_name"], "url": item["page_url"]}
            for item in config["featured"]
        ],
    }
    text = json.dumps(data, ensure_ascii=False, indent=2).replace("</", "<\\/")
    return f'  <script type="application/ld+json">\n{text}\n  </script>'


def site_header(home: str, nav: list[tuple[str, str]], asset_base: str) -> str:
    anchors = "".join(f'<a href="{href}">{escape(label)}</a>' for href, label in nav)
    nav_html = f'\n      <nav class="po-nav" aria-label="Primary navigation">{anchors}</nav>' if nav else ""
    return f'''  <a class="hub-skip" href="#main">Skip to content</a>
  <header class="po-header">
    <div class="po-shell po-header__inner">
      <a class="po-brand" href="{home}"><img src="{asset_base}favicon.svg" width="28" height="28" alt=""><span>Eduardo Pin</span></a>{nav_html}
      <a class="po-header__gh" href="https://github.com/eduardopin">{GITHUB_ICON}<span>GitHub</span></a>
    </div>
  </header>'''


def hero() -> str:
    return f'''    <section class="po-hero" id="top" aria-labelledby="hero-title">
      <div class="po-art" aria-hidden="true"><div class="po-art__haze"></div>{TRACE_SVG}<div class="po-art__veil"></div></div>
      <div class="po-shell po-hero__grid">
        <div class="po-hero__copy">
          <p class="po-label po-hero__eyebrow">Cloud · Platform Engineering · SRE · FinOps · DevSecOps</p>
          <h1 class="po-display" id="hero-title">Eduardo Pin</h1>
          <p class="po-hero__lede">Public-safe examples, operational guidance and a small set of developer tools.</p>
          <div class="po-hero__actions">
            <a class="po-btn po-btn--primary" href="#featured">Explore featured projects</a>
            <a class="po-btn po-btn--ghost" href="https://github.com/eduardopin">{GITHUB_ICON}GitHub profile</a>
          </div>
        </div>
        <div class="po-trace-panel" aria-hidden="true">
          <p class="po-label po-trace-panel__label">profile / work index</p>
          <span class="po-trace-panel__rule"></span><span class="po-trace-panel__rule"></span><span class="po-trace-panel__rule"></span><span class="po-trace-panel__rule"></span>
        </div>
      </div>
    </section>'''


def stat_badge(word: str) -> str:
    variant = " po-stat--live" if word == "page live" else " po-stat--alpha" if word == "pre-alpha" else ""
    return f'<span class="po-stat{variant} po-label"><span class="po-stat__dot"></span>{escape(word)}</span>'


def featured_cards(featured: list[dict[str, object]], by_name: dict[str, dict[str, object]]) -> str:
    cards: list[str] = []
    for item in featured:
        name = str(item["name"])
        project = by_name[name]
        repo = str(project["url"])
        badges = stat_badge(str(item["status"]))
        if item.get("stage"):
            badges += stat_badge(str(item["stage"]))
        stars = f"https://img.shields.io/github/stars/eduardopin/{name}?style=flat&label=stars"
        cards.append(
            f'''        <article class="po-card hub-card hub-card--{escape(item["hue"])}" aria-labelledby="card-{escape(name)}">
          <div class="po-card__top"><span class="hub-card__badges">{badges}</span><span class="po-label">{escape(item["details"])}</span></div>
          <div class="hub-card__id"><img src="{escape(item["mark"])}" width="28" height="28" alt=""><span class="po-card__hue" aria-hidden="true"></span></div>
          <h3 id="card-{escape(name)}"><a href="{escape(item["page_url"])}">{escape(name)}</a></h3>
          <p>{escape(item["note"])}</p>
          <div class="po-card__actions">
            <a class="po-btn po-btn--star" href="{escape(repo)}">{STAR_ICON}<span>Star on GitHub</span></a>
            <a class="hub-stars" href="{escape(repo)}"><img src="{escape(stars)}" width="76" height="20" alt="GitHub stars for {escape(name)}"></a>
            <a class="po-btn po-btn--ghost" href="{escape(repo)}">Source</a>
          </div>
          <p class="po-card__license">{escape(item["license_note"])}</p>
        </article>'''
        )
    return "\n".join(cards)


def slug(value: object) -> str:
    return str(value).lower().replace(" & ", "-").replace(" ", "-")


def project_row(project: dict[str, object], description: object, language: str, level: int = 4) -> str:
    return f'''            <li class="hub-row">
              <h{level}><a href="{escape(project["url"])}">{escape(project["name"])}</a></h{level}>
              <p>{escape(description)}</p>
              <p class="hub-row__meta"><span>{escape(language)}</span><span>no license file yet</span></p>
            </li>'''


def reference_groups(groups: list[dict[str, object]], by_name: dict[str, dict[str, object]]) -> str:
    rendered: list[str] = []
    for group in groups:
        rows = "\n".join(
            project_row(by_name[str(name)], by_name[str(name)]["description"], str(by_name[str(name)]["language"] or "Not specified"))
            for name in group["projects"]
        )
        rendered.append(
            f'''        <section class="hub-group" aria-labelledby="{escape(slug(group["name"]))}">
          <div class="hub-group__head">
            <h3 id="{escape(slug(group["name"]))}">{escape(group["name"])}</h3>
            <p>{escape(group["description"])}</p>
          </div>
          <ul class="hub-rows">
{rows}
          </ul>
        </section>'''
        )
    return "\n".join(rendered)


def older_projects(items: list[dict[str, object]], by_name: dict[str, dict[str, object]]) -> str:
    return "\n".join(
        project_row(by_name[str(item["name"])], item["note"], f'{by_name[str(item["name"])]["language"] or "SQL"} · older', level=3)
        for item in items
    )


def cross_links(config: dict[str, object], asset_base: str, include_hub: bool) -> str:
    items = []
    if include_hub:
        items.append(("rust", SITE_URL, f"{asset_base}favicon.svg", "Eduardo Pin", "All projects and reference material."))
    for item in config["featured"]:
        items.append((item["hue"], item["page_url"], f'{asset_base}{item["mark"]}', item["display_name"], item["cross_line"]))
    lis = "\n".join(
        f'''        <li class="po-cross__item hub-cross--{escape(hue)}"><a href="{escape(url)}"><img src="{escape(mark)}" width="28" height="28" alt=""><strong>{escape(name)}</strong><span>{escape(line)}</span></a></li>'''
        for hue, url, mark, name, line in items
    )
    return f'''  <section class="po-cross" aria-labelledby="cross-title">
    <div class="po-shell">
      <h2 class="po-label po-cross__head" id="cross-title">More from Eduardo Pin</h2>
      <ul class="po-cross__list">
{lis}
      </ul>
    </div>
  </section>'''


def site_footer(top_href: str) -> str:
    return f'''  <footer class="po-footer">
    <div class="po-shell po-footer__inner">
      <p>Profile hub of Eduardo Pin, generated from this repository's data files. No analytics.</p>
      <nav aria-label="Footer navigation"><a href="https://github.com/eduardopin">GitHub profile</a><a href="https://github.com/eduardopin/eduardopin">Source of this page</a><a href="{top_href}">Back to top</a></nav>
    </div>
  </footer>'''


def build_index(config: dict[str, object], by_name: dict[str, dict[str, object]]) -> str:
    nav = [("#featured", "Featured"), ("#references", "References"), ("#older", "Older"), ("#contact", "Contact")]
    return f'''<!doctype html>
<html lang="en">
<head>
{head(TITLE, DESCRIPTION, asset_base="", canonical=SITE_URL, noindex=False)}
{json_ld(config)}
</head>
<body>
{site_header("#top", nav, "")}

  <main id="main">
{hero()}

    <section class="hub-section" id="featured" aria-labelledby="featured-title">
      <div class="po-shell">
        <div class="hub-section__head">
          <h2 id="featured-title">Featured projects</h2>
          <p>Current work, with status and licensing stated plainly.</p>
        </div>
        <div class="hub-cards">
{featured_cards(config["featured"], by_name)}
        </div>
      </div>
    </section>

    <section class="hub-section" id="references" aria-labelledby="references-title">
      <div class="po-shell">
        <div class="hub-section__head">
          <h2 id="references-title">Reference examples</h2>
          <p>Public-safe examples and runbooks with generic placeholders and no proprietary details.</p>
        </div>
{reference_groups(config["reference_groups"], by_name)}
      </div>
    </section>

    <section class="hub-section" id="older" aria-labelledby="older-title">
      <div class="po-shell">
        <div class="hub-section__head">
          <h2 id="older-title">Older</h2>
          <p>SQL script libraries created in 2017, listed separately from current work.</p>
        </div>
        <ul class="hub-rows hub-rows--older">
{older_projects(config["older"], by_name)}
        </ul>
      </div>
    </section>

    <section class="hub-section hub-contact" id="contact" aria-labelledby="contact-title">
      <div class="po-shell">
        <h2 id="contact-title">Continue on GitHub</h2>
        <p>Browse repositories, open an issue or follow updates from the profile.</p>
        <p><a class="hub-contact__link" href="https://github.com/eduardopin">github.com/eduardopin <span aria-hidden="true">↗</span></a></p>
      </div>
    </section>
  </main>

{cross_links(config, "", include_hub=False)}
{site_footer("#top")}
</body>
</html>
'''


def build_404(config: dict[str, object]) -> str:
    return f'''<!doctype html>
<html lang="en">
<head>
{head("Nothing at this address — Eduardo Pin", "This address does not exist on the Eduardo Pin hub.", asset_base=BASE_PATH, canonical=None, noindex=True)}
</head>
<body>
{site_header(BASE_PATH, [], BASE_PATH)}

  <main id="main" class="po-shell hub-404">
    <h1 class="po-display">Nothing at this address.</h1>
    <p>The link may be old or mistyped. The four pages below are the ones that exist.</p>
  </main>

{cross_links(config, BASE_PATH, include_hub=True)}
{site_footer(BASE_PATH)}
</body>
</html>
'''


def build_sitemap(config: dict[str, object]) -> str:
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        f"  <url>\n    <loc>{SITE_URL}</loc>\n    <lastmod>{escape(config['site_updated'])}</lastmod>\n  </url>\n"
        "</urlset>\n"
    )

def license_note(name: str, featured_by_name: dict[str, dict[str, object]]) -> str:
    if name in featured_by_name:
        return str(featured_by_name[name]["license_note"])
    return "No license file yet."


def readme_table(config: dict[str, object], by_name: dict[str, dict[str, object]]) -> str:
    featured_by_name = {str(item["name"]): item for item in config["featured"]}
    rows = [
        "<!-- Generated by scripts/build_hub.py. -->",
        "| Project | Area | Language | Summary | License note |",
        "| --- | --- | --- | --- | --- |",
    ]

    for item in config["featured"]:
        name = str(item["name"])
        project = by_name[name]
        area = f"Featured · {item['status']}"
        rows.append(
            f"| [{markdown_cell(name)}]({project['url']}) | {markdown_cell(area)} | "
            f"{markdown_cell(project['language'] or '—')} | {markdown_cell(item['note'])} | "
            f"{markdown_cell(license_note(name, featured_by_name))} |"
        )

    for group in config["reference_groups"]:
        for raw_name in group["projects"]:
            name = str(raw_name)
            project = by_name[name]
            rows.append(
                f"| [{markdown_cell(name)}]({project['url']}) | {markdown_cell(group['name'])} | "
                f"{markdown_cell(project['language'] or '—')} | {markdown_cell(project['description'])} | "
                f"{markdown_cell(license_note(name, featured_by_name))} |"
            )

    for item in config["older"]:
        name = str(item["name"])
        project = by_name[name]
        rows.append(
            f"| [{markdown_cell(name)}]({project['url']}) | Older | "
            f"{markdown_cell(project['language'] or '—')} | {markdown_cell(item['note'])} | "
            f"{markdown_cell(license_note(name, featured_by_name))} |"
        )
    return "\n".join(rows)


def update_readme(table: str) -> None:
    source = README_PATH.read_text(encoding="utf-8")
    if source.count(PROJECTS_START) != 1 or source.count(PROJECTS_END) != 1:
        raise ValueError("README project markers must each appear exactly once")
    before, remainder = source.split(PROJECTS_START, 1)
    _, after = remainder.split(PROJECTS_END, 1)
    output = f"{before}{PROJECTS_START}\n{table}\n{PROJECTS_END}{after}"
    README_PATH.write_text(output, encoding="utf-8", newline="\n")


def main() -> None:
    projects = load_json(PROJECTS_PATH)
    config = load_json(FEATURED_PATH)
    if not isinstance(projects, list) or not isinstance(config, dict):
        raise TypeError("Unexpected project data shape")
    by_name = project_index(projects)
    validate(projects, config, by_name)
    check_featured_licenses(config, by_name)

    INDEX_PATH.parent.mkdir(parents=True, exist_ok=True)
    INDEX_PATH.write_text(build_index(config, by_name), encoding="utf-8", newline="\n")
    NOT_FOUND_PATH.write_text(build_404(config), encoding="utf-8", newline="\n")
    SITEMAP_PATH.write_text(build_sitemap(config), encoding="utf-8", newline="\n")
    update_readme(readme_table(config, by_name))


if __name__ == "__main__":
    main()
