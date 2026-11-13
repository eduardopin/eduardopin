#!/usr/bin/env python3
"""Render site/og.png (1200x630) from HTML with headless Chrome.

The image follows the Pin Open social-image spec: ``ground`` light, the hub's
real favicon at 96px with a 64px inset, the name in Archivo 780, one 8px rule
in the hub's ``accent-fill`` (rust), the three project marks in a row, and the
URL in Martian Mono 24px in ``ink-muted``. Text stays inside the central
1080x510. No screenshot, gradient or star count.

Needs Google Chrome or Chromium (``CHROME`` overrides the binary) and network
access to Google Fonts. Standard library only; run by hand after a change and
commit the PNG.
"""

from __future__ import annotations

import json
import os
import shutil
import struct
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"
OUTPUT = SITE / "og.png"
WIDTH, HEIGHT = 1200, 630
TOKENS = ROOT / "design-system" / "tokens.json"
FONTS_URL = (
    "https://fonts.googleapis.com/css2?family=Archivo:wdth,wght@62..125,100..900"
    "&family=Martian+Mono:wdth,wght@75..112.5,100..800&display=block"
)


def light(name: str) -> str:
    tokens = json.loads(TOKENS.read_text(encoding="utf-8"))["color"]["tokens"]
    value = next(t["value"] for t in tokens if t["name"] == name)
    return value["light"]


def page() -> str:
    featured = json.loads((ROOT / "data" / "featured.json").read_text(encoding="utf-8"))["featured"]
    marks = "".join(
        f'<li><img src="{(SITE / item["mark"]).as_uri()}" width="64" height="64" alt=""><span>{item["display_name"]}</span></li>'
        for item in featured
    )
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<link rel="stylesheet" href="{FONTS_URL}">
<style>
html,body{{margin:0;width:{WIDTH}px;height:{HEIGHT}px;overflow:hidden;background:{light("ground")};color:{light("ink")};font-family:Archivo,sans-serif}}
.fav{{position:absolute;left:64px;top:64px;width:96px;height:96px}}
h1{{position:absolute;left:64px;top:196px;margin:0;font-size:72px;line-height:.94;font-weight:780;font-stretch:118%;letter-spacing:-.035em}}
.rule{{position:absolute;left:64px;top:290px;width:264px;height:8px;background:{light("rust")}}}
ul{{position:absolute;left:64px;top:350px;margin:0;padding:0;list-style:none;display:flex;gap:40px}}
li{{display:flex;align-items:center;gap:16px;font-size:26px;font-weight:650}}
li img{{display:block;width:64px;height:64px}}
.url{{position:absolute;left:64px;top:500px;font-family:"Martian Mono",monospace;font-size:24px;color:{light("ink-muted")}}}
</style></head><body>
<img class="fav" src="{(SITE / "favicon.svg").as_uri()}" alt="">
<h1>Eduardo Pin</h1><div class="rule"></div><ul>{marks}</ul>
<div class="url">eduardopin.github.io/eduardopin</div>
</body></html>"""


def chrome() -> str:
    for candidate in (os.environ.get("CHROME"), "google-chrome", "chromium", "chromium-browser"):
        if candidate and shutil.which(candidate):
            return shutil.which(candidate)  # type: ignore[return-value]
    raise SystemExit("Chrome or Chromium not found; set CHROME to its path")


def png_size(path: Path) -> tuple[int, int]:
    header = path.read_bytes()[:24]
    if header[:8] != b"\x89PNG\r\n\x1a\n":
        raise SystemExit(f"{path} is not a PNG")
    return struct.unpack(">II", header[16:24])


def main() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        html = Path(tmp) / "og.html"
        html.write_text(page(), encoding="utf-8")
        shot = Path(tmp) / "og.png"
        subprocess.run(
            [chrome(), "--headless=new", "--disable-gpu", "--hide-scrollbars", "--force-device-scale-factor=1",
             f"--window-size={WIDTH},{HEIGHT}", "--virtual-time-budget=10000", f"--user-data-dir={tmp}/profile",
             f"--screenshot={shot}", html.as_uri()],
            check=True, capture_output=True,
        )
        if png_size(shot) != (WIDTH, HEIGHT):
            raise SystemExit(f"rendered {png_size(shot)}, expected {(WIDTH, HEIGHT)}")
        shutil.copyfile(shot, OUTPUT)
    print(f"wrote {OUTPUT.relative_to(ROOT)} {WIDTH}x{HEIGHT}, {OUTPUT.stat().st_size} bytes")


if __name__ == "__main__":
    main()
