#!/usr/bin/env python3
"""Compile the Pin Open design system and check vendored copies of it.

``python3 scripts/build_ds_css.py`` reads ``design-system/tokens.json``,
``design-system/bundle.css`` and ``design-system/VERSION`` and writes
``site/assets/pin-open-<version>.css``: the tokens as custom properties, then the
component CSS. Its first line is a header naming the version, the hub commit
that last touched ``design-system/`` and the sha256 of everything after the
header line.

``python3 scripts/build_ds_css.py check <file> [--ref <git ref>]`` is the drift
check that the other pages run on their vendored copy: the body must match its
own sha256, the version must be the hub's version at the ref, and the body must
equal what the hub compiles at the ref. Standard library only.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DS_DIR = "design-system"
ASSETS = ROOT / "site" / "assets"
HEADER_RE = re.compile(
    r"^/\*! pin-open (?P<version>\d+\.\d+\.\d+) \| hub eduardopin@(?P<commit>[0-9a-f]{7,40}|dirty)"
    r" \| sha256:(?P<sha>[0-9a-f]{64}) \*/$"
)
VERSION_RE = re.compile(r"^\d+\.\d+\.\d+$")

# Per-theme multipliers of the hero light, from the tokens' opacity notes
# (dark: lines x1.65, haze x0.8, star sweep at sweep-dark).
ART_SWITCHES = {
    "light": {"art-line-filter": "none", "haze-mult": "1", "sweep-strength": "1"},
    "dark": {"art-line-filter": "brightness(1.65)", "haze-mult": "0.8", "sweep-strength": "var(--sweep-dark)"},
}


class DriftError(Exception):
    """A vendored copy does not match the hub's design system."""


def css_value(value: str) -> str:
    match = re.fullmatch(r"\{([a-z0-9-]+)\}", value)
    return f"var(--{match.group(1)})" if match else value


def themed_tokens(tokens: dict) -> list[dict]:
    themed = list(tokens["color"]["tokens"])
    themed.extend(tokens["shadow"]["tokens"])
    return themed


def static_tokens(tokens: dict) -> list[tuple[str, str]]:
    pairs: list[tuple[str, str]] = []
    for group in ("spacing", "radius", "opacity", "duration", "easing"):
        pairs.extend((t["name"], str(t["value"])) for t in tokens[group]["tokens"])
    for role, stack in tokens["type"]["families"].items():
        pairs.append((f"font-{role}", stack))
    return pairs


def theme_block(tokens: dict, theme: str) -> str:
    decls = []
    for token in themed_tokens(tokens):
        value = token["value"]
        if isinstance(value, dict):
            decls.append(f"--{token['name']}:{css_value(value[theme])}")
        elif theme == "light":
            decls.append(f"--{token['name']}:{css_value(value)}")
    decls.extend(f"--{name}:{value}" for name, value in ART_SWITCHES[theme].items())
    return ";".join(decls)


def tokens_css(tokens: dict) -> str:
    light = theme_block(tokens, "light")
    static = ";".join(f"--{name}:{value}" for name, value in static_tokens(tokens))
    dark = theme_block(tokens, "dark")
    return (
        "/* Pin Open tokens: generated from design-system/tokens.json. */\n"
        f":root{{color-scheme:light;{light};{static}}}\n"
        f'@media (prefers-color-scheme: dark){{:root:not([data-theme="light"]){{color-scheme:dark;{dark}}}}}\n'
        f':root[data-theme="dark"]{{color-scheme:dark;{dark}}}\n'
        ':root[data-theme="light"]{color-scheme:light}\n'
    )


def compile_body(tokens_text: str, bundle_text: str) -> str:
    tokens = json.loads(tokens_text)
    return tokens_css(tokens) + "\n" + bundle_text.rstrip("\n") + "\n"


def sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def render(version: str, commit: str, body: str) -> str:
    if not VERSION_RE.match(version):
        raise ValueError(f"VERSION must be MAJOR.MINOR.PATCH, got {version!r}")
    return f"/*! pin-open {version} | hub eduardopin@{commit} | sha256:{sha256(body)} */\n{body}"


def parse(text: str) -> tuple[dict[str, str], str]:
    header, _, body = text.partition("\n")
    match = HEADER_RE.match(header)
    if not match:
        raise DriftError("first line is not a pin-open header")
    return match.groupdict(), body


def git(*args: str, cwd: Path = ROOT) -> str:
    return subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True, text=True).stdout


def read_sources(ref: str | None, hub: Path = ROOT) -> tuple[str, str, str]:
    names = ("VERSION", "tokens.json", "bundle.css")
    if ref is None:
        return tuple((hub / DS_DIR / name).read_text(encoding="utf-8") for name in names)  # type: ignore[return-value]
    return tuple(git("show", f"{ref}:{DS_DIR}/{name}", cwd=hub) for name in names)  # type: ignore[return-value]


def source_commit(hub: Path = ROOT) -> str:
    if git("status", "--porcelain", "--", DS_DIR, cwd=hub).strip():
        return "dirty"
    return git("log", "-1", "--format=%h", "--", DS_DIR, cwd=hub).strip()


def build(allow_dirty: bool = False) -> Path:
    version, tokens_text, bundle_text = read_sources(None)
    version = version.strip()
    commit = source_commit()
    if commit == "dirty" and not allow_dirty:
        raise SystemExit("design-system/ has uncommitted changes; commit them first (or pass --allow-dirty)")
    output = ASSETS / f"pin-open-{version}.css"
    ASSETS.mkdir(parents=True, exist_ok=True)
    for stale in ASSETS.glob("pin-open-*.css"):
        if stale != output:
            stale.unlink()
    output.write_text(render(version, commit, compile_body(tokens_text, bundle_text)), encoding="utf-8", newline="\n")
    return output


def check_vendor(vendored: Path, ref: str | None = None, hub: Path = ROOT) -> str:
    """Return the checked version, or raise DriftError with the reason."""
    meta, body = parse(vendored.read_text(encoding="utf-8"))
    if sha256(body) != meta["sha"]:
        raise DriftError("vendored body was edited: its sha256 no longer matches the header")
    version, tokens_text, bundle_text = read_sources(ref, hub)
    version = version.strip()
    if meta["version"] != version:
        raise DriftError(f"vendored version {meta['version']} is not the hub's {version} at {ref or 'working tree'}")
    if vendored.name != f"pin-open-{version}.css":
        raise DriftError(f"file name {vendored.name} does not carry version {version}")
    if body != compile_body(tokens_text, bundle_text):
        raise DriftError(f"vendored body differs from the hub's design-system at {ref or 'working tree'}")
    return version


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command")
    build_cmd = sub.add_parser("build", help="compile site/assets/pin-open-<version>.css (default)")
    build_cmd.add_argument("--allow-dirty", action="store_true")
    check_cmd = sub.add_parser("check", help="check a vendored copy against the hub")
    check_cmd.add_argument("file", type=Path)
    check_cmd.add_argument("--ref", help="hub git ref or tag, e.g. pin-open-1.0.0 (default: working tree)")
    check_cmd.add_argument("--hub", type=Path, default=ROOT, help="hub repository root")
    args = parser.parse_args(argv)

    if args.command == "check":
        try:
            version = check_vendor(args.file, args.ref, args.hub)
        except (DriftError, OSError, subprocess.CalledProcessError) as error:
            print(f"check_vendor: FAIL {args.file}: {error}", file=sys.stderr)
            return 1
        print(f"check_vendor: OK {args.file} matches pin-open {version} at {args.ref or 'working tree'}")
        return 0

    output = build(getattr(args, "allow_dirty", False))
    print(f"wrote {output.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
