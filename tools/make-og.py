#!/usr/bin/env python3
"""Build og.png - the 1200x630 card Discord and other unfurlers show for this site.

Why this file exists: the link is pasted into Discord, and Discord (like X, Slack,
iMessage and Facebook) will not render an SVG preview. og:image used to point at
logo.svg, so every shared link unfurled as bare text. Discord also wants a raster
image at least 1200x630, which is what this produces.

Rerun after any brand change:  python tools/make-og.py
Fonts come from the DTF app's embedded set so the card matches the site's Geist.
"""

import os
from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.dirname(HERE)
FONT_DIR = os.path.join(os.path.dirname(SITE), "DTF", "Fonts")

W, H = 1200, 630
BG = (4, 4, 7, 255)
PURPLE = (168, 85, 247)
PURPLE_DEEP = (124, 58, 237)
TXT = (244, 244, 247, 255)
MUT = (141, 141, 153, 255)
DIM = (92, 92, 104, 255)

MARGIN_X = 88
COL_W = 470                      # left column width; must stay clear of the frame
FRAME_W = 504
FRAME_X = W - MARGIN_X - FRAME_W  # right edge aligned to the margin


def font(name, size):
    return ImageFont.truetype(os.path.join(FONT_DIR, name), size)


def tracked(draw, xy, text, fnt, fill, tracking=0.0, anchor="la"):
    """Draw text with letter-spacing - Pillow has no tracking of its own."""
    x, y = xy
    total = sum(fnt.getlength(c) for c in text) + tracking * max(len(text) - 1, 0)
    if anchor[0] == "m":
        x -= total / 2
    elif anchor[0] == "r":
        x -= total
    for c in text:
        draw.text((x, y), c, font=fnt, fill=fill)
        x += fnt.getlength(c) + tracking
    return total


def rounded_mask(size, radius):
    m = Image.new("L", size, 0)
    ImageDraw.Draw(m).rounded_rectangle([0, 0, size[0] - 1, size[1] - 1], radius, fill=255)
    return m


def main():
    canvas = Image.new("RGBA", (W, H), BG)
    draw = ImageDraw.Draw(canvas)
    boxes = {}

    # --- background: purple glows, matching the site's .bg-glow ---
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gd.ellipse([-260, -420, 620, 460], fill=PURPLE_DEEP + (120,))
    gd.ellipse([W - 300, H - 380, W + 320, H + 300], fill=PURPLE + (70,))
    canvas.alpha_composite(glow.filter(ImageFilter.GaussianBlur(140)))

    # --- faint grid, faded out towards the bottom, as on the site ---
    grid = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    grd = ImageDraw.Draw(grid)
    for x in range(0, W, 74):
        grd.line([(x, 0), (x, H)], fill=(255, 255, 255, 12))
    for y in range(0, H, 74):
        grd.line([(0, y), (W, y)], fill=(255, 255, 255, 12))
    fade = ImageChops.invert(Image.linear_gradient("L").resize((W, H)))  # 255 top -> 0 bottom
    grid.putalpha(ImageChops.multiply(grid.getchannel("A"), fade))
    canvas.alpha_composite(grid)

    # --- right: real app screenshot in a framed window ---
    shot = Image.open(os.path.join(SITE, "screens", "main-panel.png")).convert("RGBA")
    sh = round(shot.height * FRAME_W / shot.width)
    shot = shot.resize((FRAME_W, sh), Image.LANCZOS)
    fy = (H - sh) // 2

    # Fade the bottom of the panel out, the same trick site.css uses on .mock img.
    # Without it the crop slices the app's own "Ready" status line mid-glyph.
    fade_start = int(sh * 0.78)
    fade = Image.new("L", (FRAME_W, sh), 255)
    fd = ImageDraw.Draw(fade)
    for y in range(fade_start, sh):
        fd.line([(0, y), (FRAME_W, y)],
                fill=int(255 - 200 * (y - fade_start) / max(sh - fade_start, 1)))

    shadow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(shadow).rounded_rectangle(
        [FRAME_X - 6, fy + 12, FRAME_X + FRAME_W + 6, fy + sh + 26], 18, fill=(0, 0, 0, 190))
    canvas.alpha_composite(shadow.filter(ImageFilter.GaussianBlur(26)))

    canvas.paste(shot, (FRAME_X, fy),
                 ImageChops.multiply(rounded_mask((FRAME_W, sh), 14), fade))
    draw.rounded_rectangle([FRAME_X, fy, FRAME_X + FRAME_W - 1, fy + sh - 1], 14,
                           outline=(255, 255, 255, 42), width=1)
    boxes["frame"] = (FRAME_X, fy, FRAME_X + FRAME_W, fy + sh)

    # --- left: badge, wordmark, labels ---
    icon = Image.open(os.path.join(SITE, "icon.png")).convert("RGBA").resize((84, 84), Image.LANCZOS)
    canvas.paste(icon, (MARGIN_X, 92), rounded_mask((84, 84), 24))
    draw.rounded_rectangle([MARGIN_X, 92, MARGIN_X + 83, 92 + 83], 24, outline=(255, 255, 255, 46), width=1)
    boxes["badge"] = (MARGIN_X, 92, MARGIN_X + 84, 92 + 84)

    f_word = font("Geist-Bold.ttf", 88)
    tracked(draw, (MARGIN_X - 4, 196), "DTF", f_word, TXT, tracking=-2)
    boxes["wordmark"] = (MARGIN_X, 196, MARGIN_X + int(f_word.getlength("DTF")), 196 + 100)

    f_kick = font("GeistMono-Medium.ttf", 19)
    tracked(draw, (MARGIN_X, 306), "PC CLEANER PLATFORM", f_kick, PURPLE + (255,), tracking=4.4)
    boxes["kicker"] = (MARGIN_X, 306, MARGIN_X + COL_W, 306 + 24)

    draw.line([(MARGIN_X, 352), (MARGIN_X + 74, 352)], fill=(255, 255, 255, 60), width=1)

    f_lead = font("Geist-SemiBold.ttf", 33)
    draw.text((MARGIN_X, 378), "Premium Windows tools.", font=f_lead, fill=TXT)
    boxes["lead"] = (MARGIN_X, 378, MARGIN_X + int(f_lead.getlength("Premium Windows tools.")), 378 + 42)

    f_sub = font("Geist-Regular.ttf", 25)
    for i, line in enumerate(["The most updated cleaner on the",
                              "market. One click, zero traces left."]):
        draw.text((MARGIN_X, 432 + i * 34), line, font=f_sub, fill=MUT)
        boxes[f"sub{i}"] = (MARGIN_X, 432 + i * 34, MARGIN_X + int(f_sub.getlength(line)), 432 + i * 34 + 32)

    f_foot = font("GeistMono-Regular.ttf", 17)
    # Two short lines rather than one long one: the full domain next to the OS
    # details ran past the screenshot column (caught by the checks below).
    for i, line in enumerate(["Windows 10 / 11  ·  64-bit", "dtfshop-shoavey.vercel.app"]):
        y = 548 + i * 26
        draw.text((MARGIN_X, y), line, font=f_foot, fill=DIM)
        boxes[f"footer{i}"] = (MARGIN_X, y, MARGIN_X + int(f_foot.getlength(line)), y + 22)

    # --- self-check: nothing may leave the canvas or collide with the frame ---
    problems = []
    for name, (x0, y0, x1, y1) in boxes.items():
        if x0 < 0 or y0 < 0 or x1 > W or y1 > H:
            problems.append(f"{name} leaves the canvas: {x1 - x0}x{y1 - y0} at ({x0},{y0})")
        if name != "frame" and x1 > FRAME_X - 24:
            problems.append(f"{name} reaches into the screenshot column (right edge {x1}, frame starts {FRAME_X})")
    if shot.width != FRAME_W:
        problems.append("screenshot width mismatch")

    out = os.path.join(SITE, "og.png")
    canvas.convert("RGB").save(out, "PNG", optimize=True)

    # Ink check: a bbox can be correct while the glyphs never landed (wrong font path,
    # wrong fill). So measure bright pixels inside each element's box, on the saved file.
    with Image.open(out) as chk:
        ink = ImageChops.invert(chk.convert("L"))
        for name, (x0, y0, x1, y1) in boxes.items():
            box = ink.crop((x0, y0, x1, y1))
            bright = sum(1 for p in box.tobytes() if p > 60)
            frac = bright / max((x1 - x0) * (y1 - y0), 1)
            floor = 0.06 if name == "frame" else 0.005
            if frac < floor:
                problems.append(f"{name} looks empty: only {frac:.3%} of its box is lit (expected >= {floor:.1%})")
        cov = chk.convert("RGB").resize((120, 63))
        distinct = len(cov.getcolors(maxcolors=200000) or [])
    print(f"wrote {out}")
    print(f"  size {chk.width}x{chk.height}, {os.path.getsize(out) / 1024:.0f} KB, ~{distinct} distinct colours in a 120x63 sample")
    print(f"  screenshot lane: x {FRAME_X}..{FRAME_X + FRAME_W}, y {fy}..{fy + sh}")
    for name, b in boxes.items():
        print(f"  {name:<9} {b}")
    if problems:
        raise SystemExit("LAYOUT PROBLEMS:\n  " + "\n  ".join(problems))
    print("  layout checks passed")


if __name__ == "__main__":
    main()
