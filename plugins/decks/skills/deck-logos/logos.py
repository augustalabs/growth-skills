#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["pillow>=11", "playwright>=1.48", "numpy>=1.26", "scipy>=1.11"]
# ///
"""Logo candidates for Augusta decks: find them, clean them, show them, pick one.

Two kinds of logo:

  wordmark  the company's horizontal logo, for the lockups next to Augusta's logo
            (cover, company divider, thank-you)
  mark      a square symbol, for the small portfolio-company tiles (PE deep dives)

Cleaning keeps the logo's own colours. Colour on the slide (white, ink, grey) is
applied in Paper with CSS, so all we need here is a transparent, tightly trimmed
file:

  SVG     full-canvas background shapes are removed; the viewBox is trimmed to the
          painted ink (rendered in headless Chromium). A PNG render is written too.
  raster  PNG / JPG / WebP / ICO. A transparent image keeps its alpha; an opaque one
          has its background colour sampled from the border and keyed out with a
          soft edge. An app-icon plate (a solid rounded square on transparency) is
          keyed out the same way, leaving the symbol. Trimmed to the ink.

Every candidate is then checked on its rendered pixels. Blocking flags:

  busy_background   the border isn't one flat colour, keying it out eats the mark
  solid_block       the result is mostly a filled rectangle
  boxed_logo        the mark sits inside a filled box
  knockout_detail   white shapes over colour that could not be cut out; made one
                    colour, that detail disappears
  empty             nothing left after background removal
  low_resolution    too small to render sharp at twice the slot size
Knockouts (white letters or shapes painted over colour, like a badge) are cut out
automatically, the way a brand prints its logo in one colour: the white becomes
transparent. Such candidates carry the note `knockout_cut`.

Non-blocking notes (they rank a candidate down, they don't rule it out):
  knockout_cut      white parts were cut out (see above); check it reads right
  detail_lost       colours that touch each other (a pin on a disc, triangles in a
                    symbol) merge into one shape in one colour; pick it only if the
                    one-colour preview still reads as the logo
  boxed             the logo is a filled box with the name cut out of it; prefer an
                    unboxed version when the company has one
  stacked           (wordmark) symbol-over-name layout, weak next to Augusta's
                    one-line logo; use it only when no horizontal version exists
  not_square        (mark) the company's standard logo, not a square symbol; the
                    fallback when the company has no symbol and no site icon

Run with uv, which installs the dependencies above on first use (and Chromium, once):
  uv run logos.py ...

Usage:
  logos.py collect --run <run> --company "Acme" --domain acme.com --kind wordmark|mark
                   [--role client|fund|portco] [--extra FILE_URL ...] [--no-site]
      Finds candidates on the company's own site (rendered header logo, schema.org
      logo, apple-touch icon, icons, favicon) plus any --extra file URLs, cleans and
      checks each, and writes <run>/logos/<company>-<kind>/candidates.json + sheet.png.
      Run again with more --extra (and --no-site) to append; numbering continues and
      failed downloads are retried.
  logos.py pick <dir> <n> --reason "..." [--accept low_resolution]
      Records candidate n: <dir>/logo.png (+ logo.svg when vector) and choice.json,
      with the confidence worked out. Only low_resolution can be accepted.
  logos.py none <dir> --reason "..."
      Records that no acceptable logo exists (the deck keeps its placeholder).
  logos.py report --run <run>
      Writes <run>/logos/logos.json from every pick / none.
"""
from __future__ import annotations

import argparse
import base64
import html
import io
import json
import re
import shutil
import time
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path

from PIL import Image, ImageChops, ImageFilter, ImageStat

# Augusta's logo, from the Paper templates (the same file the decks use). Only used to
# preview each candidate in the lockup next to it.
AUGUSTA_LOGO_URL = "https://app.paper.design/file-assets/01M39QHEHME0CT0WQVYB9WFFWA/7RYEQ2KH2FHAJH0TT686E4E0PX.png"

UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/140 Safari/537.36")
MAX_DOWNLOAD = 8 * 1024 * 1024
RENDER_PX = 1200            # long side of SVG renders used for checks and logo.png
KEY_LO, KEY_HI = 18.0, 70.0  # background key ramp (max channel distance)
# busy background: share of the border that is far from the background colour. A photo or
# gradient backdrop is far all round; JPEG noise or a mark touching the edge is not.
BUSY_BORDER_SHARE = 0.25
BUSY_BORDER_DIST = 40
BUSY_BORDER_TONES = 12
SOLID_FILL = 0.82
BOX_EDGE_FILL = 0.9
TRIM_ALPHA = 10
# Margin kept around the trimmed ink, as a share of EACH side's own length. A share of
# the long side made wide wordmarks render short in their slot (the old deck bot's bug).
MARGIN = 0.02
# Minimum ink size in px: the lockup slot is ~56px tall, the tile mark ~27px; both
# must stay sharp at 2x.
MIN_WORDMARK_H = 110
MIN_MARK_SIDE = 54
MARK_ASPECT = (0.6, 1.67)      # fits the square tile; wider/taller is a wordmark
STACKED_BELOW = 1.5
BLOCKING = {"busy_background", "solid_block", "boxed_logo", "knockout_detail",
            "empty", "low_resolution", "download_failed", "not_an_image"}

SVG_NS = "http://www.w3.org/2000/svg"
NON_PAINTED = {"clipPath", "mask", "pattern", "marker", "symbol", "defs",
               "linearGradient", "radialGradient"}


# ---------------------------------------------------------------- browser

class Browser:
    """One headless Chromium for the whole run."""
    _pw = _browser = None

    @classmethod
    def page(cls, **kw):
        if cls._browser is None:
            from playwright.sync_api import sync_playwright
            cls._pw = sync_playwright().start()
            try:
                cls._browser = cls._pw.chromium.launch()
            except Exception:  # noqa: BLE001 — first run on this machine: fetch Chromium once
                import subprocess
                import sys
                subprocess.run([sys.executable, "-m", "playwright", "install", "chromium"], check=True)
                cls._browser = cls._pw.chromium.launch()
        return cls._browser.new_context(user_agent=UA, **kw).new_page()

    @classmethod
    def close(cls):
        if cls._browser:
            cls._browser.close()
            cls._pw.stop()
            cls._browser = cls._pw = None


def render_svg(svg: bytes, long_side: int = RENDER_PX, viewbox=None) -> Image.Image | None:
    """Rasterise an SVG (transparent background) at `long_side` px."""
    vb = viewbox or svg_viewbox(svg)
    if not vb or vb[2] <= 0 or vb[3] <= 0:
        return None
    scale = long_side / max(vb[2], vb[3])
    w, h = max(1, round(vb[2] * scale)), max(1, round(vb[3] * scale))
    src = "data:image/svg+xml;base64," + base64.b64encode(svg).decode()
    page = Browser.page()
    try:
        data = page.evaluate("""async ([src, w, h]) => {
            const img = new Image(); img.src = src; await img.decode();
            const c = document.createElement('canvas'); c.width = w; c.height = h;
            c.getContext('2d').drawImage(img, 0, 0, w, h);
            return c.toDataURL('image/png');
        }""", [src, w, h])
    except Exception:  # noqa: BLE001 — a broken SVG just fails to render
        return None
    finally:
        page.context.close()
    return Image.open(io.BytesIO(base64.b64decode(data.split(",", 1)[1]))).convert("RGBA")


# ---------------------------------------------------------------- site scan

SCAN_JS = r"""(company) => {
  const out = [], seen = new Set();
  const add = (o) => { const k = o.url || o.svg; if (k && !seen.has(k)) { seen.add(k); out.push(o); } };
  const abs = (u) => { try { return new URL(u, location.href).href; } catch { return null; } };
  const words = (el) => [el.id, el.getAttribute('class'), el.getAttribute('alt'),
                         el.getAttribute('aria-label'), el.getAttribute('title'),
                         el.closest('a') && el.closest('a').getAttribute('aria-label')]
                        .join(' ').toLowerCase();
  const co = (company || '').toLowerCase();
  const homeLink = (el) => { const a = el.closest('a'); if (!a) return false;
    try { const u = new URL(a.href, location.href); return u.host === location.host && (u.pathname === '/' || u.pathname === ''); }
    catch { return false; } };
  const inHeader = (el) => !!el.closest('header, nav, [class*="header" i], [id*="header" i], [role="banner"]');
  const score = (el) => {
    const w = words(el), home = homeLink(el), named = w.includes('logo') || (co && w.includes(co));
    const r0 = el.getBoundingClientRect();
    // page imagery is never a logo candidate: it must be labelled as a logo / the company
    // or link home, and be logo-sized
    if ((!home && !named) || r0.width > 600 || r0.height > 250) return 0;
    // small UI icons (arrows, search, menu) sit in headers and home links too
    if (!w.includes('logo') && r0.width < 40 && r0.height < 40) return 0;
    if (/linkedin|facebook|instagram|youtube|twitter|spotify|apple|google|podcast|tiktok|x-logo|social/.test(w + ' ' + (el.getAttribute('src') || ''))) return 0;
    if (!home && !w.includes('logo') && !inHeader(el) && r0.top > 250) return 0;   // a name alone counts only up top
    let s = 0;
    if (named) s += 3; if (co && w.includes(co)) s += 2;
    if (home) s += 3; if (inHeader(el)) s += 2;
    const r = el.getBoundingClientRect(); if (r.top < 200 && r.width > 20) s += 1;
    return s;
  };
  const inlineSvg = (svg) => {
    const c = svg.cloneNode(true);
    c.setAttribute('xmlns', 'http://www.w3.org/2000/svg');
    // pull in sprite symbols referenced by <use>
    const defs = document.createElementNS('http://www.w3.org/2000/svg', 'defs');
    c.querySelectorAll('use').forEach(u => {
      const ref = (u.getAttribute('href') || u.getAttribute('xlink:href') || '');
      if (ref.startsWith('#')) { const t = document.getElementById(ref.slice(1)); if (t) defs.appendChild(t.cloneNode(true)); }
    });
    if (defs.childNodes.length) c.insertBefore(defs, c.firstChild);
    if (!c.getAttribute('viewBox')) {
      try { const b = svg.getBBox(); if (b.width && b.height) c.setAttribute('viewBox', `${b.x} ${b.y} ${b.width} ${b.height}`); } catch {}
    }
    // resolve currentColor to the rendered colour so the file stands alone
    const col = getComputedStyle(svg).color;
    return c.outerHTML.replace(/currentColor/g, col);
  };
  document.querySelectorAll('svg').forEach(svg => {
    const s = score(svg); if (s >= 4) add({origin: 'site-header-svg', score: s, svg: inlineSvg(svg)});
  });
  const biggest = (img) => {
    const set = (img.getAttribute('srcset') || '').split(',').map(x => x.trim().split(/\s+/))
      .filter(x => x[0]).map(x => [x[0], parseFloat(x[1]) || 1]);
    set.sort((a, b) => b[1] - a[1]);
    return set.length ? set[0][0] : (img.currentSrc || img.src);
  };
  document.querySelectorAll('img').forEach(img => {
    const s = score(img); const u = abs(biggest(img));
    if (s >= 4 && u) add({origin: 'site-header-img', score: s, url: u});
  });
  document.querySelectorAll('script[type="application/ld+json"]').forEach(sc => {
    try {
      const walk = (o) => { if (!o || typeof o !== 'object') return;
        if (o.logo) { const l = typeof o.logo === 'string' ? o.logo : (o.logo.url || o.logo.contentUrl); if (l) add({origin: 'schema-logo', score: 5, url: abs(l)}); }
        Object.values(o).forEach(walk); };
      walk(JSON.parse(sc.textContent));
    } catch {}
  });
  document.querySelectorAll('link[rel]').forEach(l => {
    const rel = l.rel.toLowerCase(), u = abs(l.getAttribute('href'));
    if (!u) return;
    if (rel.includes('apple-touch-icon')) add({origin: 'apple-touch-icon', score: 4, url: u});
    else if (rel.includes('mask-icon')) add({origin: 'mask-icon', score: 3, url: u});
    else if (rel.includes('icon')) add({origin: 'icon', score: 2, sizes: l.getAttribute('sizes') || '', url: u});
  });
  add({origin: 'favicon', score: 1, url: abs('/favicon.ico')});
  return out;
}"""


ICON_ORIGINS = {"apple-touch-icon", "mask-icon", "icon", "favicon"}


def _browser_get(page, url: str) -> bytes | None:
    """Fetch a file in the site's own browser session: first as a request, then by
    opening it like a visitor would (some sites block everything else)."""
    try:
        r = page.request.get(url, timeout=20000)
        if r.ok:
            return r.body()
    except Exception:  # noqa: BLE001
        pass
    tab = page.context.new_page()
    try:
        r = tab.goto(url, timeout=20000)
        if r and r.ok:
            return r.body()
    except Exception:  # noqa: BLE001
        pass
    finally:
        tab.close()
    return None


def scan_site(domain: str, company: str, kind: str) -> list[dict]:
    """Load the site in a real browser and list its logo candidates. Files are
    downloaded through the same browser session: many sites refuse plain downloads."""
    url = domain if domain.startswith("http") else f"https://{domain}"
    page = Browser.page(viewport={"width": 1440, "height": 900}, device_scale_factor=2)
    found = []
    try:
        page.goto(url, wait_until="domcontentloaded", timeout=30000)
        page.wait_for_timeout(2500)
        found = page.evaluate(SCAN_JS, company)
        if kind == "wordmark":
            found = [f for f in found if f["origin"] not in ICON_ORIGINS]
        for f in found:
            if f.get("url"):
                body = _browser_get(page, f["url"])
                if body:
                    f["data"] = base64.b64encode(body[:MAX_DOWNLOAD]).decode()
    except Exception as e:  # noqa: BLE001
        print(f"site scan failed for {url}: {type(e).__name__}: {str(e)[:120]}")
    finally:
        page.context.close()
    return sorted(found, key=lambda f: -f.get("score", 0))


# ---------------------------------------------------------------- fetch

def direct_url(url: str) -> str:
    """A Wikimedia/Wikipedia `File:` page -> the file itself."""
    m = re.match(r"https?://([^/]*wiki[mp]edia\.org)/wiki/(?:File|Ficheiro|Archivo|Datei|Fichier):(.+)", url)
    return f"https://{m.group(1)}/wiki/Special:FilePath/{m.group(2)}" if m else url


def fetch(src: str) -> bytes:
    p = Path(src).expanduser()
    if not src.startswith(("http://", "https://", "data:")) and p.exists():
        return p.read_bytes()
    if src.startswith("data:"):
        head, _, body = src.partition(",")
        return base64.b64decode(body) if ";base64" in head else urllib.parse.unquote(body).encode()
    req = urllib.request.Request(direct_url(src), headers={"User-Agent": UA, "Accept": "image/*,*/*;q=0.5"})
    for wait in (3, 8, 20, None):          # rate limits (Wikimedia answers 429): back off, retry
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                data = r.read(MAX_DOWNLOAD + 1)
            break
        except urllib.error.HTTPError as e:
            if e.code != 429 or wait is None:
                raise
            time.sleep(int(e.headers.get("Retry-After") or wait))
    if len(data) > MAX_DOWNLOAD:
        raise ValueError("larger than 8 MB")
    if data[:4] == b"PK\x03\x04":
        data = from_zip(data)
    return data


def from_zip(data: bytes) -> bytes:
    """Brand kits ship as .zip: take the first SVG, else the largest raster."""
    with zipfile.ZipFile(io.BytesIO(data)) as z:
        names = [n for n in z.namelist() if not n.startswith("__MACOSX") and not n.endswith("/")]
        svgs = [n for n in names if n.lower().endswith(".svg")]
        if svgs:
            return z.read(svgs[0])
        rasters = [n for n in names if n.lower().endswith((".png", ".webp", ".jpg", ".jpeg"))]
        if not rasters:
            raise ValueError("zip holds no image")
        return z.read(max(rasters, key=lambda n: z.getinfo(n).file_size))


def sniff(data: bytes) -> str | None:
    head = data[:600].lstrip().lower()
    if head.startswith(b"<svg") or (head.startswith(b"<?xml") and b"<svg" in data[:4000].lower()):
        return "svg"
    if head.startswith((b"<!doctype", b"<html")):
        return None
    try:
        return Image.open(io.BytesIO(data)).format.lower()
    except Exception:  # noqa: BLE001
        return None


# ---------------------------------------------------------------- clean: svg

def _num(v):
    m = re.match(r"\s*(-?[\d.]+)", v or "")
    return float(m.group(1)) if m else None


def svg_viewbox(svg: bytes):
    try:
        root = ET.fromstring(svg)
    except ET.ParseError:
        return None
    vb = root.get("viewBox")
    if vb:
        parts = [float(p) for p in re.split(r"[\s,]+", vb.strip()) if p]
        if len(parts) == 4:
            return tuple(parts)
    w, h = _num(root.get("width")), _num(root.get("height"))
    return (0.0, 0.0, w, h) if w and h else None


_KNOWN_NS = {"xlink": "http://www.w3.org/1999/xlink", "xml": None}


def fix_namespaces(data: bytes) -> bytes:
    """Inline SVGs lifted from a page often use prefixes (xlink:href, sketch:type ...)
    without declaring them, which XML parsers refuse. Declare xlink; drop the rest."""
    text = data.decode("utf-8", "replace")
    used = set(re.findall(r"[\s<]([A-Za-z][\w-]*):[A-Za-z][\w-]*\s*=", text)) - {"xmlns"}
    for pre in used:
        if f"xmlns:{pre}=" in text or pre == "xml":
            continue
        if pre in _KNOWN_NS:
            text = re.sub(r"<svg\b", f'<svg xmlns:{pre}="{_KNOWN_NS[pre]}"', text, count=1)
        else:
            text = re.sub(rf"\s{pre}:[\w-]+\s*=\s*(\"[^\"]*\"|'[^']*')", "", text)
    return text.encode()


def clean_svg(data: bytes) -> tuple[bytes, Image.Image | None, list[str], str]:
    """Remove full-canvas background shapes, trim the viewBox to the ink.
    Returns (svg bytes, render, problems, background note)."""
    ET.register_namespace("", SVG_NS)
    ET.register_namespace("xlink", "http://www.w3.org/1999/xlink")
    data = fix_namespaces(data)
    root = ET.fromstring(data)
    problems, note = [], "transparent"
    vb = svg_viewbox(data)
    parents = {c: p for p in root.iter() for c in p}

    def hidden(el):
        while el in parents:
            el = parents[el]
            if el.tag.split("}")[-1] in NON_PAINTED:
                return True
        return False

    removed = 0
    for el in list(root.iter()):
        if el.tag.split("}")[-1] == "rect" and vb and not hidden(el) and not el.get("clip-path"):
            w, h = _num(el.get("width")), _num(el.get("height"))
            if w and h and w >= 0.95 * vb[2] and h >= 0.95 * vb[3]:
                parents[el].remove(el)
                removed += 1
    if removed:
        note = f"{removed} background shape(s) removed"
    for attr in ("width", "height"):
        root.attrib.pop(attr, None)
    svg = ET.tostring(root, encoding="utf-8")
    if not vb:
        return svg, None, ["empty"], note
    im = render_svg(svg, viewbox=vb)
    if im is None or not im.getchannel("A").getbbox():
        return svg, im, ["empty"], note
    # trim: ink box in viewBox units, plus the per-side margin
    x0, y0, x1, y1 = im.getchannel("A").point(lambda a: 255 if a > TRIM_ALPHA else 0).getbbox()
    sx, sy = vb[2] / im.width, vb[3] / im.height
    w, h = (x1 - x0) * sx, (y1 - y0) * sy
    nvb = (vb[0] + x0 * sx - w * MARGIN, vb[1] + y0 * sy - h * MARGIN, w * (1 + 2 * MARGIN), h * (1 + 2 * MARGIN))
    root.set("viewBox", " ".join(f"{v:.3f}" for v in nvb))
    svg = ET.tostring(root, encoding="utf-8")
    return svg, render_svg(svg, viewbox=nvb), problems, note


# ---------------------------------------------------------------- clean: raster

def _border(im: Image.Image, band: int) -> list[tuple]:
    w, h = im.size
    px = im.load()
    pts = []
    for x in range(0, w, max(1, w // 200)):
        for y in list(range(band)) + list(range(h - band, h)):
            pts.append(px[x, y])
    for y in range(0, h, max(1, h // 200)):
        for x in list(range(band)) + list(range(w - band, w)):
            pts.append(px[x, y])
    return pts


def _key_out(rgba: Image.Image, bg: tuple) -> Image.Image:
    """Alpha from distance to `bg` (max channel difference), soft edge."""
    r, g, b = (ch.point(lambda v, c=c: abs(v - c)) for ch, c in zip(rgba.convert("RGB").split(), bg))
    dist = ImageChops.lighter(ImageChops.lighter(r, g), b)
    alpha = dist.point(lambda d: 0 if d <= KEY_LO else 255 if d >= KEY_HI
                       else int(255 * (d - KEY_LO) / (KEY_HI - KEY_LO)))
    return ImageChops.multiply(alpha, rgba.getchannel("A"))


def _dominant_opaque(rgba: Image.Image) -> tuple:
    small = rgba.copy()
    small.thumbnail((64, 64))
    opaque = [p[:3] for p in (small.get_flattened_data() if hasattr(small, "get_flattened_data") else small.getdata()) if p[3] > 200]
    return max(set(opaque), key=opaque.count) if opaque else (255, 255, 255)


def open_raster(data: bytes) -> Image.Image:
    im = Image.open(io.BytesIO(data))
    if im.format == "ICO":
        sizes = sorted(im.ico.sizes(), key=lambda s: s[0] * s[1])
        im = im.ico.getimage(sizes[-1])
    im.load()
    return im.convert("RGBA")


def clean_raster(data: bytes) -> tuple[Image.Image, list[str], str]:
    rgba = open_raster(data)
    w, h = rgba.size
    problems, note = [], "transparent"
    border = _border(rgba, max(2, min(w, h) // 50))
    transparent = sum(1 for p in border if p[3] < 30) / len(border)
    if transparent > 0.6:
        alpha = rgba.getchannel("A")
        # An app-icon plate (solid rounded square on transparency): key out the plate.
        mask = alpha.point(lambda a: 255 if a > 128 else 0)
        bbox = mask.getbbox()
        if bbox and ImageStat.Stat(mask.crop(bbox)).mean[0] / 255 > SOLID_FILL:
            plate = _dominant_opaque(rgba)
            keyed = _key_out(rgba, plate)
            if keyed.getbbox():
                alpha, note = keyed, "icon plate #%02x%02x%02x removed" % plate
    else:
        opaque = [p for p in border if p[3] >= 30]
        bg = tuple(sorted(c[i] for c in opaque)[len(opaque) // 2] for i in range(3))
        far = [c for c in opaque if max(abs(c[i] - bg[i]) for i in range(3)) > BUSY_BORDER_DIST]
        # A mark that bleeds to the edge also puts colour on the border, but only its own
        # few flat colours; a photo or gradient backdrop brings many.
        tones = {tuple(v // 32 for v in c[:3]) for c in far}
        if len(far) / len(opaque) > BUSY_BORDER_SHARE and len(tones) > BUSY_BORDER_TONES:
            problems.append("busy_background")
        alpha = _key_out(rgba, bg)
        note = "#%02x%02x%02x removed" % bg
    out = rgba.copy()
    out.putalpha(alpha)
    bbox = alpha.point(lambda a: 255 if a > TRIM_ALPHA else 0).getbbox()
    if bbox is None:
        return out, problems + ["empty"], note
    x0, y0, x1, y1 = bbox
    mx, my = int((x1 - x0) * MARGIN), int((y1 - y0) * MARGIN)
    out = out.crop((max(0, x0 - mx), max(0, y0 - my), min(w, x1 + mx), min(h, y1 + my)))
    return out, problems, note


# ---------------------------------------------------------------- checks

def _edge_fill(mask: Image.Image) -> float:
    bbox = mask.getbbox()
    if not bbox:
        return 0.0
    x0, y0, x1, y1 = bbox
    px, i = mask.load(), 2
    edge = [px[x, y0 + i] for x in range(x0, x1)] + [px[x, y1 - 1 - i] for x in range(x0, x1)]
    edge += [px[x0 + i, y] for y in range(y0, y1)] + [px[x1 - 1 - i, y] for y in range(y0, y1)]
    return sum(1 for v in edge if v) / len(edge)


def cut_knockouts(im: Image.Image) -> tuple[Image.Image, bool]:
    """White shapes painted over colour (letters in a badge, bars in a circle) become
    transparent, so the logo survives being made one colour. White that is set apart
    from the colour (a white tagline on transparency) is left alone."""
    import numpy as np
    from scipy import ndimage

    a = np.asarray(im.convert("RGBA")).copy()
    opaque = a[..., 3] > 200
    lo = a[..., :3].min(axis=2)
    white = opaque & (lo > 235)
    colour = opaque & (lo <= 200)
    if white.sum() < 0.02 * opaque.sum() or colour.sum() < 0.10 * opaque.sum():
        return im, False
    labels, n = ndimage.label(white, structure=np.ones((3, 3)))
    if not n:
        return im, False
    cut = np.zeros_like(white)
    for i, sl in enumerate(ndimage.find_objects(labels), start=1):
        y0, y1 = max(sl[0].start - 2, 0), sl[0].stop + 2
        x0, x1 = max(sl[1].start - 2, 0), sl[1].stop + 2
        comp = labels[y0:y1, x0:x1] == i
        ring = ndimage.binary_dilation(comp, iterations=2) & ~comp
        if not ring.any():
            continue
        on_colour = (colour[y0:y1, x0:x1] & ring).sum() / ring.sum()
        if on_colour > 0.5:
            cut[y0:y1, x0:x1] |= comp
    if not cut.any():
        return im, False
    # take the anti-aliased light edge with it
    edge = ndimage.binary_dilation(cut, iterations=2) & (lo > 200)
    a[cut | edge, 3] = 0
    return Image.fromarray(a, "RGBA"), True


def detail_lost(im: Image.Image) -> bool:
    """Share of the logo's drawing that is colour-against-colour. Made one colour, those
    borders vanish: a pin on a disc becomes a dot, a tri-colour symbol a solid block.
    Gradients change gently and don't count; only hard borders between colours do."""
    import numpy as np
    from scipy import ndimage

    small = im.copy()
    small.thumbnail((400, 400))
    a = np.asarray(small.convert("RGBA")).astype(int)
    opaque = a[..., 3] > 200
    if opaque.sum() < 50:
        return False
    rgb = a[..., :3]
    # hard colour borders inside the ink
    dx = np.abs(rgb[:, 1:] - rgb[:, :-1]).max(axis=2) > 70
    dy = np.abs(rgb[1:] - rgb[:-1]).max(axis=2) > 70
    inner = np.zeros(opaque.shape, bool)
    inner[:, 1:] |= dx & opaque[:, 1:] & opaque[:, :-1]
    inner[1:] |= dy & opaque[1:] & opaque[:-1]
    inner &= ndimage.binary_erosion(opaque, iterations=2)   # not the outline's anti-aliasing
    outline = opaque & ~ndimage.binary_erosion(opaque)
    # judged per shape: a small tri-colour symbol next to a long wordmark still counts
    labels, n = ndimage.label(ndimage.binary_dilation(opaque, iterations=1))
    total = opaque.sum()
    for i in range(1, n + 1):
        comp = labels == i
        if (comp & opaque).sum() < 0.03 * total:
            continue
        if (inner & comp).sum() > 0.25 * max((outline & comp).sum(), 1):
            return True
    return False


def check(im: Image.Image, kind: str, vector: bool) -> tuple[list[str], float]:
    problems = []
    alpha = im.getchannel("A")
    mask = alpha.point(lambda a: 255 if a > 128 else 0)
    if not mask.getbbox():
        return ["empty"], 0.0
    aspect = round(im.width / im.height, 3)
    if ImageStat.Stat(mask).mean[0] / 255 > SOLID_FILL:
        problems.append("solid_block")
    if _edge_fill(mask) > BOX_EDGE_FILL:
        problems.append("boxed_logo")
    # knockout: white shapes over colour disappear when the logo becomes one colour
    # (white that sits ON colour; white next to colour, like a white tagline, is fine)
    small = im.copy()
    small.thumbnail((300, 300))
    r, g, b, a = small.split()
    lo = ImageChops.darker(ImageChops.darker(r, g), b)            # min channel
    opaque = a.point(lambda v: 255 if v > 200 else 0)
    white = ImageChops.multiply(lo.point(lambda v: 255 if v > 235 else 0), opaque)
    colour = ImageChops.multiply(lo.point(lambda v: 255 if v <= 200 else 0), opaque)
    ink = ImageStat.Stat(opaque).sum[0] / 255
    n_white = ImageStat.Stat(white).sum[0] / 255
    n_colour = ImageStat.Stat(colour).sum[0] / 255
    if ink and n_white / ink > 0.04 and n_colour / ink > 0.10:
        # the outline of the white shapes: how much of it runs along colour? A white
        # tagline set apart from the colour is outlined by transparency; a white letter
        # on a coloured shape is outlined by colour.
        edge = ImageChops.subtract(white, white.filter(ImageFilter.MinFilter(3)))
        near = colour.filter(ImageFilter.MaxFilter(5))
        n_edge = ImageStat.Stat(edge).sum[0] / 255
        if n_edge and ImageStat.Stat(ImageChops.multiply(edge, near)).sum[0] / 255 / n_edge > 0.3:
            problems.append("knockout_detail")
    if detail_lost(im):
        problems.append("detail_lost")
    if not vector:
        if kind == "wordmark" and im.height < MIN_WORDMARK_H:
            problems.append("low_resolution")
        if kind == "mark" and min(im.size) < MIN_MARK_SIDE:
            problems.append("low_resolution")
    if kind == "mark" and not (MARK_ASPECT[0] <= aspect <= MARK_ASPECT[1]):
        problems.append("not_square")
    if kind == "wordmark" and aspect < STACKED_BELOW:
        problems.append("stacked")
    return problems, aspect


# ---------------------------------------------------------------- collect

def process(src: dict, n: int, kind: str, cdir: Path) -> dict:
    entry = {"n": n, "origin": src.get("origin", "extra"), "source": src.get("url") or src.get("file") or "inline svg"}
    try:
        if src.get("svg"):
            data = src["svg"].encode()
        elif src.get("data"):
            data = base64.b64decode(src["data"])
            if data[:4] == b"PK\x03\x04":
                data = from_zip(data)
        else:
            data = fetch(src.get("url") or src["file"])
    except Exception as e:  # noqa: BLE001
        entry.update(problems=["download_failed"], error=f"{type(e).__name__}: {e}"[:160])
        return entry
    fmt = sniff(data)
    if fmt is None:
        entry.update(problems=["not_an_image"], error="not an image (a web page?) — pass the file's URL")
        return entry
    stem = cdir / f"{n:02d}"
    try:
        if fmt == "svg":
            svg, im, problems, note = clean_svg(data)
            stem.with_suffix(".svg").write_bytes(svg)
            entry["svg"] = str(stem.with_suffix(".svg"))
            vector = True
        else:
            im, problems, note = clean_raster(data)
            vector = False
    except Exception as e:  # noqa: BLE001
        entry.update(problems=["not_an_image"], error=f"{type(e).__name__}: {e}"[:160])
        return entry
    if im is not None and "empty" not in problems:
        im, was_cut = cut_knockouts(im)
        if was_cut:
            # the cut exists only as pixels: the PNG (rendered large) is the file to use
            problems.append("knockout_cut")
            if vector:
                entry.pop("svg", None)
                stem.with_suffix(".svg").unlink(missing_ok=True)
        im.save(stem.with_suffix(".png"))
        entry["png"] = str(stem.with_suffix(".png"))
        more, aspect = check(im, kind, vector and not was_cut)
        if was_cut and "boxed_logo" in more:
            # a filled box with the name cut out is a legitimate reversed logo
            more = ["boxed" if m == "boxed_logo" else m for m in more if m != "solid_block"]
        problems = list(dict.fromkeys(problems + more))
        entry.update(aspect=aspect, size=list(im.size))
    entry.update(format=fmt, vector=vector, background=note, problems=problems)
    return entry


def collect(kind: str, out: Path, domain: str | None, company: str, extras: list[str], site: bool,
            role: str = "") -> list[dict]:
    cdir = out / "candidates"
    cdir.mkdir(parents=True, exist_ok=True)
    path = out / "candidates.json"
    entries = json.loads(path.read_text()) if path.exists() else []
    # a failed download can be retried: only sources that worked count as known
    known = {e["source"] for e in entries if not e.get("error")}
    sources = []
    if site and domain:
        found = scan_site(domain, company, kind)
        if not found:
            print("WARNING: the site scan found no candidates (the site may block automated browsers)."
                  " Go to step 4: add sources with --extra.")
        sources += found
    sources += [{"origin": "extra", ("url" if x.startswith(("http", "data:")) else "file"): x} for x in extras]
    n = max([e["n"] for e in entries] + [0])
    for src in sources:
        key = src.get("url") or src.get("file") or src.get("svg")
        if key in known:
            continue
        known.add(key)
        n += 1
        entries.append(process(src, n, kind, cdir))
    path.write_text(json.dumps(entries, indent=1) + "\n")
    (out / "meta.json").write_text(json.dumps({"company": company, "role": role, "kind": kind, "domain": domain},
                                              indent=1, ensure_ascii=False) + "\n")
    if not sheet(entries, kind, out / "sheet.png"):
        print("WARNING: no usable candidate yet, so no sheet. Add sources with --extra.")
    return entries


# ---------------------------------------------------------------- contact sheet

def _uri(p: Path) -> str:
    mime = "image/svg+xml" if p.suffix == ".svg" else "image/png"
    return f"data:{mime};base64,{base64.b64encode(p.read_bytes()).decode()}"


def sheet(entries: list[dict], kind: str, out: Path) -> Path | None:
    """One row per usable candidate, shown as it will sit on the slide:
    wordmark -> white next to Augusta's logo on the dark cover; mark -> ink in the 42px
    tile. Plus the original colours, to judge identity."""
    rows = []
    aug = AUGUSTA_LOGO_URL
    for e in entries:
        img = e.get("svg") or e.get("png")
        flags = e.get("problems") or []
        bad = [f for f in flags if f in BLOCKING]
        tag = (f"<b style='color:#e5484d'>{', '.join(bad)}</b> " if bad else "") + \
              " ".join(f for f in flags if f not in BLOCKING)
        meta = (f"<b>#{e['n']}</b> {html.escape(e['origin'])} · {e.get('format', '?')}"
                f"{' · aspect ' + str(e['aspect']) if e.get('aspect') else ''}<br>"
                f"<small>{html.escape(e['source'][:80])}</small><br><small>{tag or 'ok'}</small>")
        if not img:
            rows.append(f"<div class='row'><div class='meta'>{meta}<br><small>{html.escape(e.get('error', ''))}</small></div></div>")
            continue
        src = _uri(Path(img))
        if kind == "wordmark":
            slot = ("<div class='cell dark'>"
                    + (f"<img src='{aug}' style='height:40px'>" if aug else "<span>Augusta Labs</span>")
                    + "<div class='div'></div>"
                    f"<div class='slotbox'><img src='{src}' class='white'></div></div>")
        else:
            slot = (f"<div class='cell light'><div class='tile'><img src='{src}' class='ink'"
                    " style='max-width:27px;max-height:27px'></div>"
                    f"<div class='tile big'><img src='{src}' class='ink' style='max-width:58px;max-height:58px'></div></div>")
        orig = f"<div class='cell grey'><img src='{src}' style='max-height:70px;max-width:300px'></div>"
        rows.append(f"<div class='row'><div class='meta'>{meta}</div>{slot}{orig}</div>")
    if not rows:
        return None
    page_html = f"""<html><head><style>
      body{{margin:0;padding:16px;font:12px -apple-system,Helvetica,sans-serif;background:#f4f4f5;width:1300px}}
      .row{{display:flex;gap:12px;align-items:center;margin-bottom:10px}}
      .meta{{width:330px;color:#27272a;overflow-wrap:anywhere}}
      .cell{{width:400px;height:110px;display:flex;align-items:center;justify-content:center;gap:16px;border-radius:8px}}
      .dark{{background:#020202;width:500px}} .grey{{background:#dcdce0}} .light{{background:#F9F9F9;border:1px solid #E5E7F0}}
      .div{{width:3px;height:44px;background:#464646;flex-shrink:0}} .dark img{{flex-shrink:0}}
      .slotbox{{width:186px;height:40px;display:flex;align-items:center;justify-content:flex-start;flex-shrink:0}}
      .slotbox img{{max-width:100%;max-height:100%;object-fit:contain}} .dark span{{color:#fff;font-size:20px}}
      .white{{filter:brightness(0) invert(1)}} .ink{{filter:brightness(0);opacity:.85}}
      .tile{{width:42px;height:42px;background:#fff;border:1px solid #E5E7F0;border-radius:10px;
             display:flex;align-items:center;justify-content:center}}
      .tile.big{{width:90px;height:90px;border-radius:21px}}
    </style></head><body>{''.join(rows)}</body></html>"""
    page = Browser.page(viewport={"width": 1332, "height": 200})
    try:
        page.set_content(page_html, wait_until="networkidle", timeout=30000)
        page.screenshot(path=str(out), full_page=True)
    finally:
        page.context.close()
    return out


# ---------------------------------------------------------------- pick

ACCEPTABLE = {"low_resolution"}      # the only blocking flag a pick may accept


def _official(source: str, origin: str, domain: str | None) -> bool:
    if origin.startswith("site-") or origin in ("schema-logo", "apple-touch-icon", "mask-icon", "icon", "favicon"):
        return True
    host = urllib.parse.urlparse(source).hostname or ""
    d = (domain or "").lower().removeprefix("https://").removeprefix("http://").removeprefix("www.").split("/")[0]
    return bool(d) and (host == d or host.endswith("." + d))


def pick(out: Path, n: int, accept: set[str], reason: str) -> dict:
    entries = {e["n"]: e for e in json.loads((out / "candidates.json").read_text())}
    meta = json.loads((out / "meta.json").read_text()) if (out / "meta.json").exists() else {}
    if n not in entries:
        raise SystemExit(f"no candidate #{n}")
    e = entries[n]
    if accept - ACCEPTABLE:
        raise SystemExit(f"only {', '.join(sorted(ACCEPTABLE))} can be accepted; "
                         f"{', '.join(sorted(accept - ACCEPTABLE))} means the logo breaks on the slide")
    blocking = [p for p in e.get("problems", []) if p in BLOCKING and p not in accept]
    if blocking or not e.get("png"):
        raise SystemExit(f"candidate #{n} is not usable: {', '.join(blocking) or e.get('error', 'no file')}"
                         " (accept a flag with --accept only if the sheet shows it is fine)")
    shutil.copy(e["png"], out / "logo.png")
    if e.get("svg"):
        shutil.copy(e["svg"], out / "logo.svg")
    notes = [p for p in e.get("problems", []) if p not in BLOCKING]
    accepted = sorted(set(e.get("problems", [])) & accept)
    official = _official(e["source"], e["origin"], meta.get("domain"))
    lowering = [x for x in notes if x != "knockout_cut"]      # a clean cut is the normal treatment
    confidence = "high" if official and not accepted and not lowering else "medium"
    choice = {**meta, "n": n, "source": e["source"], "origin": e["origin"], "confidence": confidence,
              "file": str(out / ("logo.svg" if e.get("svg") else "logo.png")),
              "png": str(out / "logo.png"), "aspect": e.get("aspect"),
              "accepted": accepted, "notes": notes,
              "reason": reason + ("" if official else " (third-party source)")}
    (out / "choice.json").write_text(json.dumps(choice, indent=1) + "\n")
    (out / "none.json").unlink(missing_ok=True)
    return choice


def none(out: Path, reason: str) -> dict:
    """Record that no acceptable logo exists: the deck keeps its placeholder."""
    meta = json.loads((out / "meta.json").read_text()) if (out / "meta.json").exists() else {}
    rec = {**meta, "none": reason}
    (out / "none.json").write_text(json.dumps(rec, indent=1) + "\n")
    (out / "choice.json").unlink(missing_ok=True)
    return rec


def report(run: Path) -> Path:
    """Assemble <run>/logos/logos.json from every entry's choice.json / none.json."""
    rows = []
    for d in sorted((run / "logos").iterdir()):
        for name in ("choice.json", "none.json"):
            f = d / name
            if f.exists():
                r = json.loads(f.read_text())
                keep = ("company", "role", "kind", "n", "origin", "file", "png", "aspect", "source",
                        "confidence", "notes", "reason", "none")
                rows.append({k: r[k] for k in keep if k in r})
    missing = [d.name for d in (run / "logos").iterdir() if d.is_dir()
               and not (d / "choice.json").exists() and not (d / "none.json").exists()]
    if missing:
        print("WARNING: no pick and no none for: " + ", ".join(missing))
    out = run / "logos" / "logos.json"
    out.write_text(json.dumps(rows, indent=1, ensure_ascii=False) + "\n")
    return out


def slug(company: str) -> str:
    s = unicodedata.normalize("NFKD", company).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", "-", s).strip("-")


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("collect")
    c.add_argument("--kind", choices=["wordmark", "mark"], required=True)
    c.add_argument("--run", required=True, help="the deck run folder; files go to <run>/logos/<company>-<kind>")
    c.add_argument("--domain")
    c.add_argument("--company", required=True)
    c.add_argument("--role", default="", choices=["", "client", "fund", "portco"])
    c.add_argument("--extra", nargs="*", default=[])
    c.add_argument("--no-site", action="store_true")
    p = sub.add_parser("pick")
    p.add_argument("dir")
    p.add_argument("n", type=int)
    p.add_argument("--accept", nargs="*", default=[], choices=sorted(ACCEPTABLE))
    p.add_argument("--reason", required=True)
    no = sub.add_parser("none")
    no.add_argument("dir")
    no.add_argument("--reason", required=True)
    r = sub.add_parser("report")
    r.add_argument("--run", required=True)
    a = ap.parse_args()
    try:
        if a.cmd == "collect":
            out = Path(a.run) / "logos" / f"{slug(a.company)}-{a.kind}"
            for e in collect(a.kind, out, a.domain, a.company, a.extra, not a.no_site, a.role):
                state = ", ".join(e.get("problems") or []) or "ok"
                print(f"#{e['n']:<3} {e['origin']:<18} {state:<34} {e['source'][:70]}")
            print(f"dir:   {out}")
            if (out / "sheet.png").exists():
                print(f"sheet: {out / 'sheet.png'}")
        elif a.cmd == "pick":
            print(json.dumps(pick(Path(a.dir), a.n, set(a.accept), a.reason), indent=1))
        elif a.cmd == "none":
            print(json.dumps(none(Path(a.dir), a.reason), indent=1))
        else:
            print(report(Path(a.run)))
    finally:
        Browser.close()


if __name__ == "__main__":
    main()
