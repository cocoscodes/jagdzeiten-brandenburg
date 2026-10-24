"""Build the public site (GitHub Pages) from src.html.
Usage: python3 build.py <src.html> <out_dir>
Writes: index.html, manifest.webmanifest, icon-192.png, icon-512.png, apple-touch-icon.png, og.png, .nojekyll
Also writes artifact.html next to src (src with QR inlined) for the claude.ai artifact.
"""
import sys, os, json, io
import qrcode, qrcode.image.svg
from PIL import Image, ImageDraw, ImageFont

URL = "https://cocoscodes.github.io/jagdzeiten-brandenburg/"
GREEN, PAPER, INK, RUST = (62,118,80), (236,235,225), (34,39,29), (161,80,45)
SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

src_path, out = sys.argv[1], sys.argv[2]
os.makedirs(out, exist_ok=True)
src = open(src_path, encoding="utf-8").read()

# QR as inline SVG (black on white box)
img = qrcode.make(URL, image_factory=qrcode.image.svg.SvgPathImage, border=0, error_correction=qrcode.constants.ERROR_CORRECT_M)
buf = io.BytesIO(); img.save(buf)
svg = buf.getvalue().decode()
svg = svg[svg.index("<svg"):]
svg = svg.replace('<svg ', '<svg role="img" aria-label="QR-Code" ', 1)
svg = svg.replace('width="', 'data-w="', 1).replace('height="', 'data-h="', 1)
page = src.replace("<!--QR-->", svg)
open(os.path.join(os.path.dirname(src_path), "artifact.html"), "w", encoding="utf-8").write(page)

def icon(size):
    im = Image.new("RGB", (size, size), GREEN)
    d = ImageDraw.Draw(im)
    s = size
    # timeline motif: three bars and a "today" line
    for i, (a, b) in enumerate([(.16, .78), (.34, .84), (.22, .62)]):
        y = s*(.30 + i*.17)
        d.rounded_rectangle([s*a, y, s*b, y + s*.095], radius=s*.03, fill=PAPER)
    x = s*.57
    d.rectangle([x - s*.018, s*.20, x + s*.018, s*.80], fill=RUST)
    return im
for n in (192, 512):
    icon(n).save(os.path.join(out, f"icon-{n}.png"))
icon(180).save(os.path.join(out, "apple-touch-icon.png"))

# Open Graph preview 1200x630
og = Image.new("RGB", (1200, 630), PAPER)
d = ImageDraw.Draw(og)
d.text((80, 90), "JAGDJAHR 1. APRIL – 31. MÄRZ", font=ImageFont.truetype(SANS, 26), fill=(127,97,38))
d.text((80, 140), "Jagdzeiten\nBrandenburg", font=ImageFont.truetype(SERIF, 96), fill=INK, spacing=10)
d.text((80, 390), "Was ist heute offen? Alle Wildarten auf einer Zeitachse.", font=ImageFont.truetype(SANS, 30), fill=(90,94,77))
for i, (a, b) in enumerate([(80, 760), (300, 1000), (160, 620), (420, 1120)]):
    y = 470 + i*30
    d.rounded_rectangle([a, y, b, y+18], radius=6, fill=GREEN)
d.rectangle([698, 455, 703, 600], fill=RUST)
og.save(os.path.join(out, "og.png"))

manifest = {
  "name": "Jagdzeiten Brandenburg", "short_name": "Jagdzeiten",
  "start_url": "./", "scope": "./", "display": "standalone",
  "background_color": "#ecebe1", "theme_color": "#3e7650", "lang": "de",
  "icons": [{"src": "icon-192.png", "sizes": "192x192", "type": "image/png"},
            {"src": "icon-512.png", "sizes": "512x512", "type": "image/png"},
            {"src": "icon-512.png", "sizes": "512x512", "type": "image/png", "purpose": "maskable"}]
}
json.dump(manifest, open(os.path.join(out, "manifest.webmanifest"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)

desc = "Was ist heute offen? Alle Jagd- und Schonzeiten in Brandenburg auf einer Zeitachse, mit Countdown und Sonnenzeiten."
head = f"""<!doctype html>
<html lang="de">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<meta name="description" content="{desc}">
<meta name="theme-color" content="#3e7650">
<link rel="manifest" href="manifest.webmanifest">
<link rel="icon" type="image/png" sizes="192x192" href="icon-192.png">
<link rel="apple-touch-icon" href="apple-touch-icon.png">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-title" content="Jagdzeiten">
<meta property="og:type" content="website">
<meta property="og:title" content="Jagdzeiten Brandenburg">
<meta property="og:description" content="{desc}">
<meta property="og:url" content="{URL}">
<meta property="og:image" content="{URL}og.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<style>:root{{color-scheme:light;padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px)}}img{{max-width:100%}}[hidden]{{display:none!important}}</style>
"""
body = page.replace('<meta name="claude:viewport-fit-sides" content="cover">\n', "")
# split: everything up to the first non-head element goes in head
cut = body.index('<div class="wrap">')
html = head + body[:cut] + "</head>\n<body>\n" + body[cut:] + "\n</body>\n</html>\n"
open(os.path.join(out, "index.html"), "w", encoding="utf-8").write(html)
open(os.path.join(out, ".nojekyll"), "w").close()
print("built", out)
