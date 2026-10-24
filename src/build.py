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
repo_root = os.path.dirname(os.path.dirname(os.path.abspath(src_path)))
LOGO = open(os.path.join(repo_root, "logo.svg"), encoding="utf-8").read()
logo_inline = LOGO[LOGO.index("<svg"):].replace('role="img"', 'focusable="false"', 1)
page = src.replace("<!--QR-->", svg).replace("<!--LOGO-->", logo_inline)

# Fonts: never load from Google. Public site uses files in fonts/, the claude.ai copy embeds them.
import base64, re
FONTS = [("Source Serif 4", 600, "SourceSerif4-Semibold.ttf"), ("Source Serif 4", 700, "SourceSerif4-Bold.ttf"),
         ("Public Sans", 400, "public-sans-latin-400-normal"), ("Public Sans", 500, "public-sans-latin-500-normal"),
         ("Public Sans", 600, "public-sans-latin-600-normal"),
         ("JetBrains Mono", 400, "jetbrains-mono-latin-400-normal"), ("JetBrains Mono", 500, "jetbrains-mono-latin-500-normal")]
repo = os.path.dirname(os.path.dirname(os.path.abspath(src_path)))
def face_css(url_for):
    return "<style>/* Fonts under the SIL Open Font License 1.1 (https://openfontlicense.org): Source Serif 4 (c) 2014-2023 Adobe, Reserved Font Name 'Source', unmodified official build; Public Sans (c) 2015 The Public Sans Project Authors; JetBrains Mono (c) 2020 The JetBrains Mono Project Authors. Licence texts: fonts/OFL-*.txt in the repository. */" + "".join(
        f'@font-face{{font-family:"{fam}";font-style:normal;font-weight:{w};font-display:swap;src:url({url_for(f)}) format("woff2")}}'
        for fam, w, f in FONTS) + "</style>"
gf = re.compile(r'<link rel="stylesheet" href="https://fonts\.googleapis\.com[^>]*>')
assert gf.search(page), "Google Fonts link not found"
def data_uri(f):
    return "data:font/woff2;base64," + base64.b64encode(open(os.path.join(repo, "fonts", f + ".woff2"), "rb").read()).decode()
artifact = gf.sub(lambda m: face_css(data_uri), page)
page = gf.sub(lambda m: face_css(lambda f: f"fonts/{f}.woff2"), page)
open(os.path.join(os.path.dirname(src_path), "artifact.html"), "w", encoding="utf-8").write(artifact)

def icon(size):
    import cairosvg
    pad = int(size * 0.14)
    art = LOGO.replace("currentColor", "#f3f2e8")
    png = cairosvg.svg2png(bytestring=art.encode(), output_width=size - 2*pad, output_height=size - 2*pad)
    im = Image.new("RGB", (size, size), GREEN)
    logo = Image.open(io.BytesIO(png)).convert("RGBA")
    im.paste(logo, (pad, pad), logo)
    return im
for n in (192, 512):
    icon(n).save(os.path.join(out, f"icon-{n}.png"))
icon(180).save(os.path.join(out, "apple-touch-icon.png"))

# Open Graph preview 1200x630
og = Image.new("RGB", (1200, 630), PAPER)
d = ImageDraw.Draw(og)
d.text((80, 90), "JAGDJAHR 1. APRIL – 31. MÄRZ", font=ImageFont.truetype(SANS, 26), fill=(127,97,38))
d.text((80, 140), "Jagdzeiten\nBrandenburg", font=ImageFont.truetype(SERIF, 96), fill=INK, spacing=10)
d.text((80, 390), "Was ist heute offen? Alle Jagd- und Schonzeiten auf einen Blick.", font=ImageFont.truetype(SANS, 30), fill=(90,94,77))
# month-tile motif (as on the page): rows of 12 tiles, fill height = share of the month open
LINE = (196, 192, 170)
rows = [[1,1,1,1,1,1,1,1,1,.5,0,0], [0,0,0,0,1,1,1,1,1,.5,0,0], [0,0,0,0,0,0,1,1,1,.5,0,0], [0,0,0,0,0,1,1,1,1,1,.9,0]]
for ri, row in enumerate(rows):
    for k, f in enumerate(row):
        x0, y0 = 80 + k*58, 462 + ri*36
        x1, y1 = x0 + 52, y0 + 28
        d.rounded_rectangle([x0, y0, x1, y1], radius=5, outline=(RUST if k == 6 else LINE), width=(3 if k == 6 else 2), fill=PAPER)
        if f:
            d.rounded_rectangle([x0+2, y1 - int(26*f), x1-2, y1-2], radius=3, fill=GREEN)
import cairosvg as _c
_l = Image.open(io.BytesIO(_c.svg2png(bytestring=LOGO.replace("currentColor", "#22271d").encode(), output_width=300, output_height=300))).convert("RGBA")
og.paste(_l, (850, 60), _l)
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
<meta name="robots" content="noindex, nofollow">
<meta name="googlebot" content="noindex, nofollow">
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
