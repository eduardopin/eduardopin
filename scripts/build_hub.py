#!/usr/bin/env python3
"""Build the portfolio hub and the generated profile README project table.

Project facts live in ``data/projects.json`` and the small editorial layer lives
in ``data/featured.json``. When a project page goes live, edit its ``page_url``
and related status in ``data/featured.json``, then run ``python3
scripts/build_hub.py``. The script uses only the Python standard library and
writes ``site/index.html`` plus the content between the project markers in
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


def featured_cards(
    featured: list[dict[str, object]], by_name: dict[str, dict[str, object]]
) -> str:
    cards: list[str] = []
    for item in featured:
        project = by_name[str(item["name"])]
        destination = item["page_url"] or project["url"]
        source_link = (
            f'\n          <p class="card-links"><a href="{escape(project["url"])}">Source on GitHub</a></p>'
            if item["page_url"]
            else ""
        )
        cards.append(
            f'''        <article class="feature-card">
          <div class="card-topline">
            <span class="status">{escape(item["status"])}</span>
            <span class="language">{escape(item["details"])}</span>
          </div>
          <h3><a href="{escape(destination)}">{escape(project["name"])}</a></h3>
          <p>{escape(item["note"])}</p>
          <p class="license-note">{escape(item["license_note"])}</p>{source_link}
        </article>'''
        )
    return "\n".join(cards)


def reference_groups(
    groups: list[dict[str, object]], by_name: dict[str, dict[str, object]]
) -> str:
    rendered: list[str] = []
    for group in groups:
        rows: list[str] = []
        for name in group["projects"]:
            project = by_name[str(name)]
            rows.append(
                f'''              <li class="project-row">
                <h4><a href="{escape(project["url"])}">{escape(project["name"])}</a></h4>
                <p>{escape(project["description"])}</p>
                <div class="project-meta">
                  <span>{escape(project["language"] or "Not specified")}</span>
                  <span class="license-label">no license file yet</span>
                </div>
              </li>'''
            )
        rendered.append(
            f'''        <section class="theme-group" aria-labelledby="{escape(str(group["name"]).lower().replace(" & ", "-").replace(" ", "-"))}">
          <div class="theme-heading">
            <p class="section-index" aria-hidden="true">{len(rendered) + 1:02d}</p>
            <div>
              <h3 id="{escape(str(group["name"]).lower().replace(" & ", "-").replace(" ", "-"))}">{escape(group["name"])}</h3>
              <p>{escape(group["description"])}</p>
            </div>
          </div>
          <ul class="project-list">
{chr(10).join(rows)}
          </ul>
        </section>'''
        )
    return "\n".join(rendered)


def older_projects(
    items: list[dict[str, object]], by_name: dict[str, dict[str, object]]
) -> str:
    cards: list[str] = []
    for item in items:
        name = str(item["name"])
        project = by_name[name]
        language = project["language"] or "SQL"
        cards.append(
            f'''          <li class="older-card">
            <h3><a href="{escape(project["url"])}">{escape(project["name"])}</a></h3>
            <p>{escape(item["note"])}</p>
            <div class="project-meta">
              <span>{escape(language)} · older</span>
              <span class="license-label">no license file yet</span>
            </div>
          </li>'''
        )
    return "\n".join(cards)


def build_index(config: dict[str, object], by_name: dict[str, dict[str, object]]) -> str:
    cards = featured_cards(config["featured"], by_name)
    groups = reference_groups(config["reference_groups"], by_name)
    older = older_projects(config["older"], by_name)
    return f'''<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Eduardo Pin — Portfolio hub</title>
  <meta name="description" content="Public-safe projects and operational references across Cloud, Platform Engineering, SRE, FinOps and DevSecOps.">
  <link rel="canonical" href="https://eduardopin.github.io/eduardopin/">
  <link rel="icon" href="favicon.svg" type="image/svg+xml">
  <meta property="og:type" content="website">
  <meta property="og:title" content="Eduardo Pin — Portfolio hub">
  <meta property="og:description" content="Projects and operational references across Cloud, Platform Engineering, SRE, FinOps and DevSecOps.">
  <meta property="og:url" content="https://eduardopin.github.io/eduardopin/">
  <meta property="og:image" content="https://eduardopin.github.io/eduardopin/og.png">
  <meta property="og:image:width" content="1280">
  <meta property="og:image:height" content="640">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="Eduardo Pin — Portfolio hub">
  <meta name="twitter:description" content="Projects and operational references across Cloud, Platform Engineering, SRE, FinOps and DevSecOps.">
  <meta name="twitter:image" content="https://eduardopin.github.io/eduardopin/og.png">
  <link rel="stylesheet" href="styles.css">
</head>
<body>
  <a class="skip-link" href="#main">Skip to content</a>
  <header class="site-header">
    <a class="monogram" href="#top" aria-label="Back to top">EP</a>
    <nav aria-label="Primary navigation">
      <a href="#featured">Featured</a>
      <a href="#references">References</a>
      <a href="#older">Older</a>
      <a href="#contact">Contact</a>
    </nav>
  </header>

  <main id="main">
    <section class="hero" id="top" aria-labelledby="hero-title">
      <div class="hero-copy">
        <p class="eyebrow">Cloud · Platform Engineering · SRE · FinOps · DevSecOps</p>
        <h1 id="hero-title">Eduardo Pin</h1>
        <p class="hero-line">Public-safe examples, operational guidance and a small set of developer tools.</p>
        <div class="hero-actions">
          <a class="button button-primary" href="#featured">Explore featured projects</a>
          <a class="button button-secondary" href="https://github.com/eduardopin">GitHub profile</a>
        </div>
      </div>
      <div class="signal" aria-hidden="true">
        <span class="signal-label">profile / work index</span>
        <span class="signal-line signal-line-wide"></span>
        <span class="signal-line"></span>
        <span class="signal-line signal-line-short"></span>
        <span class="signal-dot"></span>
      </div>
    </section>

    <section class="section featured" id="featured" aria-labelledby="featured-title">
      <div class="section-heading">
        <p class="kicker">Start here</p>
        <h2 id="featured-title">Featured projects</h2>
        <p>Current work, with status and licensing stated plainly.</p>
      </div>
      <div class="feature-grid">
{cards}
      </div>
    </section>

    <section class="section references" id="references" aria-labelledby="references-title">
      <div class="section-heading">
        <p class="kicker">Working material</p>
        <h2 id="references-title">Reference examples</h2>
        <p>Public-safe examples and runbooks with generic placeholders and no proprietary details.</p>
      </div>
      <div class="theme-stack">
{groups}
      </div>
    </section>

    <section class="section older" id="older" aria-labelledby="older-title">
      <div class="section-heading">
        <p class="kicker">Archive</p>
        <h2 id="older-title">Older</h2>
        <p>SQL script libraries created in 2017, listed separately from current work.</p>
      </div>
      <ul class="older-grid">
{older}
      </ul>
    </section>

    <section class="section contact" id="contact" aria-labelledby="contact-title">
      <p class="kicker">Contact / follow</p>
      <h2 id="contact-title">Continue on GitHub</h2>
      <p>Browse repositories, open an issue or follow updates from the profile.</p>
      <a class="text-link" href="https://github.com/eduardopin">github.com/eduardopin <span aria-hidden="true">→</span></a>
    </section>
  </main>

  <footer>
    <p>GitHub profile and project navigation for Eduardo Pin.</p>
  </footer>
</body>
</html>
'''


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

    INDEX_PATH.parent.mkdir(parents=True, exist_ok=True)
    INDEX_PATH.write_text(build_index(config, by_name), encoding="utf-8", newline="\n")
    update_readme(readme_table(config, by_name))


if __name__ == "__main__":
    main()
