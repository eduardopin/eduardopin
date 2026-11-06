#!/usr/bin/env python3
"""Render the local 1280×640 social preview; requires Pillow."""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "site" / "og.png"
WIDTH = 1280
HEIGHT = 640


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    filename = "DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"
    path = Path("/usr/share/fonts/truetype/dejavu") / filename
    if path.exists():
        return ImageFont.truetype(str(path), size=size)
    return ImageFont.load_default()


def main() -> None:
    image = Image.new("RGB", (WIDTH, HEIGHT), "#10191a")
    draw = ImageDraw.Draw(image)

    draw.rectangle((0, 0, 22, HEIGHT), fill="#ef8f64")
    draw.rectangle((82, 82, 1198, 558), outline="#365052", width=2)
    draw.line((82, 180, 1198, 180), fill="#365052", width=2)
    draw.ellipse((1075, 85, 1195, 205), outline="#75c5c7", width=5)
    draw.ellipse((1120, 130, 1150, 160), fill="#ef8f64")

    draw.text((126, 112), "PORTFOLIO / WORK INDEX", font=font(24, True), fill="#75c5c7")
    draw.text((126, 238), "Eduardo Pin", font=font(76, True), fill="#f0f1ea")
    draw.text(
        (130, 348),
        "Cloud · Platform Engineering · SRE · FinOps · DevSecOps",
        font=font(29),
        fill="#cad3ce",
    )
    draw.line((130, 440, 600, 440), fill="#ef8f64", width=6)
    draw.text(
        (130, 472),
        "Projects, reference examples and operational guidance",
        font=font(24),
        fill="#9cadab",
    )

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    image.save(OUTPUT, format="PNG", optimize=False)


if __name__ == "__main__":
    main()
