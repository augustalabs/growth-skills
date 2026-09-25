#!/usr/bin/env node
// Render a deck to HTML + PDF from Paper's get_jsx output, with Chrome.
//
// Paper's own PDF export always saves to ~/Downloads and drops links, so we don't use it.
// Instead the runner saves each artboard's get_jsx({format: "inline-styles"}) to a
// file, and this script turns them into one HTML page per slide and prints it with
// headless Chrome, which keeps vector text and real <a href> links.
//
// Usage: node render.mjs <deck-dir>
//   <deck-dir>/deck.json
//     {
//       "title": "Augusta × Client",
//       "artboard": {"width": 1920, "height": 1080},
//       "fonts": ["Inter:wght@400;800", "Instrument Serif:ital@0;1"],   // Google Fonts specs
//       "slides": [
//         {"jsx": "slides/01.jsx",
//          "links": [{"x": 120, "y": 380, "w": 463, "h": 88, "url": "https://..."},
//                    {"x": 0, "y": 0, "w": 200, "h": 60, "goto": 3}]}   // 1-based slide
//       ]
//     }
//   writes <deck-dir>/deck.html and <deck-dir>/deck.pdf

import { readFileSync, writeFileSync, existsSync } from "node:fs";
import { execFileSync } from "node:child_process";
import { join, resolve } from "node:path";
import { pathToFileURL } from "node:url";

const CHROME = [
  "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
  "/Applications/Chromium.app/Contents/MacOS/Chromium",
].find(existsSync);

// CSS properties that take bare numbers (everything else numeric gets "px").
const UNITLESS = new Set([
  "fontWeight", "lineHeight", "opacity", "zIndex", "flexGrow", "flexShrink", "flex", "order",
]);

// SVG presentation attributes that React spells in camelCase.
const SVG_ATTRS = [
  "strokeWidth", "strokeLinecap", "strokeLinejoin", "strokeDasharray", "strokeDashoffset",
  "strokeMiterlimit", "strokeOpacity", "fillRule", "fillOpacity", "clipRule", "clipPath",
  "stopColor", "stopOpacity", "fontFamily", "fontSize", "fontWeight", "textAnchor",
  "dominantBaseline", "colorInterpolationFilters", "floodColor", "floodOpacity",
];

const VOID = new Set(["img", "br", "hr", "input", "meta", "link", "source"]);

const kebab = (k) => k.replace(/^(Webkit|Moz|ms)/, (m) => "-" + m.toLowerCase()).replace(/[A-Z]/g, (c) => "-" + c.toLowerCase());

// Parse the body of style={{ ... }} (a JS object literal of string/number values).
function styleToCss(body) {
  const out = [];
  const re = /\s*([A-Za-z]+)\s*:\s*(?:'((?:[^'\\]|\\.)*)'|"((?:[^"\\]|\\.)*)"|(-?[\d.]+))\s*,?/gy;
  let m;
  let pos = 0; // a failed sticky exec resets lastIndex to 0, so track progress ourselves
  while ((m = re.exec(body))) {
    pos = re.lastIndex;
    const [, key, s1, s2, num] = m;
    let val = s1 ?? s2;
    if (val === undefined) val = UNITLESS.has(key) ? num : `${num}px`;
    out.push(`${kebab(key)}: ${val.replace(/\\(.)/g, "$1")}`);
  }
  if (body.slice(pos).trim()) {
    throw new Error(`Unparsed style near: ${body.slice(pos, pos + 60)}`);
  }
  return out.join("; ");
}

const escAttr = (s) => s.replace(/&/g, "&amp;").replace(/"/g, "&quot;");

export function jsxToHtml(jsx) {
  let html = jsx.trim().replace(/^\(\s*/, "").replace(/\s*\)\s*;?$/, "");
  // Template slides carry an invisible "notion:<page id> · …" tag for Claude; never ship it.
  html = html.replace(/<div\b[^>]*>\s*notion:[^<]*<\/div>/g, "");
  html = html.replace(/style=\{\{([\s\S]*?)\}\}/g, (_, body) => `style="${escAttr(styleToCss(body))}"`);
  // Link boxes: Paper can't store links, so templates carry a transparent text layer whose
  // text is `link:<url>` (or `link:#12` for slide 12), sized over the clickable area.
  // Turn each into a real link covering the same box.
  html = html.replace(/<div\b([^>]*)>\s*link:(\S+?)\s*<\/div>/g, (_, attrs, url) =>
    `<a class="link-box" href="${escAttr(url.replace(/^#(\d+)$/, "#slide-$1"))}"${attrs}></a>`);
  // JSX drops the indentation and line breaks around text; HTML keeps them, and a
  // pre-wrap text box would show them. Apply the JSX rule: trim each line, drop blank ones.
  html = html.replace(/>([^<]*\n[^<]*)</g, (_, t) =>
    ">" + t.split("\n").map((l) => l.trim()).filter(Boolean).join(" ") + "<");
  html = html.replace(/\bclassName=/g, "class=");
  for (const a of SVG_ATTRS) html = html.replace(new RegExp(`\\b${a}=`, "g"), `${kebab(a)}=`);
  // JSX text expressions: {' '} / {"text"}
  html = html.replace(/\{\s*'((?:[^'\\]|\\.)*)'\s*\}/g, (_, s) => s.replace(/\\(.)/g, "$1"));
  html = html.replace(/\{\s*"((?:[^"\\]|\\.)*)"\s*\}/g, (_, s) => s.replace(/\\(.)/g, "$1"));
  // <div ... /> is not valid HTML outside SVG; expand self-closing non-void tags.
  // Inside <svg> the HTML parser honours self-closing, but expanding is harmless there too.
  html = html.replace(/<([a-zA-Z][\w-]*)((?:\s+[^<>]*?)?)\s*\/>/g, (all, tag, attrs) =>
    VOID.has(tag.toLowerCase()) ? `<${tag}${attrs}>` : `<${tag}${attrs}></${tag}>`);
  if (/\{[^}]*\}/.test(html.replace(/style="[^"]*"/g, ""))) {
    console.warn("warning: unconverted JSX expression left in output");
  }
  return html;
}

function fontLinks(fonts = []) {
  if (!fonts.length) return "";
  const fam = fonts.map((f) => "family=" + f.replace(/ /g, "+")).join("&");
  return `<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?${fam}&display=block">`;
}

export function buildHtml(deck, deckDir) {
  const { width: W, height: H } = deck.artboard;
  const pages = deck.slides.map((s, i) => {
    const body = jsxToHtml(readFileSync(join(deckDir, s.jsx), "utf8"));
    const links = (s.links || []).map((l) => {
      const href = l.url ? escAttr(l.url) : `#slide-${l.goto}`;
      return `<a class="hit" href="${href}" style="left:${l.x}px;top:${l.y}px;width:${l.w}px;height:${l.h}px"></a>`;
    }).join("");
    return `<section class="slide" id="slide-${i + 1}">${body}${links}</section>`;
  });
  return `<!doctype html>
<html><head><meta charset="utf-8"><title>${escAttr(deck.title || "Deck")}</title>
${fontLinks(deck.fonts)}
<style>
  @page { size: ${W}px ${H}px; margin: 0; }
  :root { --font-sans: "TWK Lausanne", system-ui, sans-serif; }
  * { box-sizing: border-box; }
  html, body { margin: 0; padding: 0; }
  body { -webkit-print-color-adjust: exact; print-color-adjust: exact; }
  .slide { position: relative; width: ${W}px; height: ${H}px; overflow: hidden; break-after: page; }
  .slide:last-child { break-after: auto; }
  /* Paper omits the artboard's own size from get_jsx; the root must fill the slide. */
  .slide > :first-child { width: ${W}px !important; height: ${H}px !important; }
  /* Paper's "hug" boxes never shrink; Chrome would squeeze them in a tight flex row and,
     with overflow-wrap: anywhere, break words letter by letter. */
  [style*="width: max-content"] { flex-shrink: 0; }
  .link-box { display: block; z-index: 2147483646; font-size: 0 !important; }
  .hit { position: absolute; display: block; z-index: 2147483647; }
  @media screen {
    body { background: #1a1a1a; display: flex; flex-direction: column; align-items: center; gap: 40px; padding: 40px 0; }
    .slide { box-shadow: 0 10px 40px rgba(0,0,0,.4); }
  }
</style></head>
<body>
${pages.join("\n")}
</body></html>`;
}

export function printPdf(htmlPath, pdfPath) {
  if (!CHROME) throw new Error("Google Chrome not found in /Applications");
  execFileSync(CHROME, [
    "--headless=new", "--disable-gpu", "--no-pdf-header-footer",
    "--virtual-time-budget=15000",            // let web fonts finish loading
    `--print-to-pdf=${pdfPath}`, pathToFileURL(htmlPath).href,
  ], { stdio: ["ignore", "ignore", "pipe"] });
}

if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) {
  const deckDir = resolve(process.argv[2] || ".");
  const deck = JSON.parse(readFileSync(join(deckDir, "deck.json"), "utf8"));
  const htmlPath = join(deckDir, "deck.html");
  const pdfPath = join(deckDir, "deck.pdf");
  writeFileSync(htmlPath, buildHtml(deck, deckDir));
  printPdf(htmlPath, pdfPath);
  console.log(`${deck.slides.length} slides -> ${htmlPath}\n${" ".repeat(String(deck.slides.length).length + 10)}-> ${pdfPath}`);
}
