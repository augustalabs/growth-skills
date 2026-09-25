#!/usr/bin/env node
// Export a whole Paper file to PDF in one command: pull every artboard's JSX straight from
// the local Paper app (the same `paper mcp` relay Claude uses), then render with render.mjs.
// No agent copies slide code by hand, so it takes seconds and the JSX is byte-exact.
//
// Usage: node export.mjs <paper-file-id> <out-dir> [--title "Deck title"]
//   Pages in the file's order; artboards on each page top to bottom, then left to right.
//   Writes <out-dir>/slides/NN.jsx, deck.json, deck.html, deck.pdf.
// Needs the Paper desktop app open, and Google Chrome.

import { spawn } from "node:child_process";
import { mkdirSync, writeFileSync } from "node:fs";
import { join, resolve } from "node:path";
import { buildHtml, printPdf } from "./render.mjs";

const [fileId, outArg, ...rest] = process.argv.slice(2);
if (!fileId || !outArg) {
  console.error('usage: node export.mjs <paper-file-id> <out-dir> [--title "Deck title"]');
  process.exit(2);
}
const ti = rest.indexOf("--title");
const title = ti >= 0 ? rest[ti + 1] : null;
const out = resolve(outArg);

const paper = spawn(process.env.HOME + "/.paper/bin/paper", ["mcp"], { stdio: ["pipe", "pipe", "inherit"] });
let buf = "";
let seq = 0;
const waiting = new Map();
paper.stdout.on("data", (d) => {
  buf += d;
  let i;
  while ((i = buf.indexOf("\n")) >= 0) {
    const line = buf.slice(0, i);
    buf = buf.slice(i + 1);
    if (!line.trim()) continue;
    const msg = JSON.parse(line);
    if (waiting.has(msg.id)) { waiting.get(msg.id)(msg); waiting.delete(msg.id); }
  }
});
const send = (m) => paper.stdin.write(JSON.stringify({ jsonrpc: "2.0", ...m }) + "\n");
const rpc = (method, params) => new Promise((res) => { const id = ++seq; waiting.set(id, res); send({ id, method, params }); });

// A tool result is a file header part plus the payload part(s).
async function call(name, args) {
  const r = await rpc("tools/call", { name, arguments: { fileId, ...args } });
  if (r.error || r.result?.isError) {
    throw new Error(`${name} ${JSON.stringify(args)}: ${JSON.stringify(r.error || r.result.content)}`);
  }
  return r.result.content.filter((c) => c.type === "text").map((c) => c.text).slice(1).join("\n");
}

try {
  await rpc("initialize", { protocolVersion: "2025-06-18", capabilities: {}, clientInfo: { name: "deck-export", version: "1" } });
  send({ method: "notifications/initialized" });

  const info = JSON.parse(await call("get_basic_info", {}));
  const slides = [];
  let size = null;
  for (const page of info.pages) {
    const p = JSON.parse(await call("get_basic_info", { pageId: page.id }));
    const boards = [...p.artboards].sort((a, b) => a.worldY - b.worldY || a.worldX - b.worldX);
    for (const a of boards) {
      size ??= { width: a.width, height: a.height };
      if (a.width !== size.width || a.height !== size.height) {
        console.warn(`skipped "${a.name}" on ${page.name}: ${a.width}x${a.height}, not a slide`);
        continue;
      }
      slides.push({ page: page.name, id: a.id, name: a.name });
    }
  }
  if (!slides.length) throw new Error("no artboards found");

  mkdirSync(join(out, "slides"), { recursive: true });
  const deck = { title: title || info.fileName, artboard: size, fonts: [], slides: [] };
  for (const [i, s] of slides.entries()) {
    const jsx = await call("get_jsx", { nodeId: s.id, format: "inline-styles" });
    const f = `slides/${String(i + 1).padStart(2, "0")}.jsx`;
    writeFileSync(join(out, f), jsx);
    deck.slides.push({ jsx: f, page: s.page, name: s.name });
  }
  writeFileSync(join(out, "deck.json"), JSON.stringify(deck, null, 2));
  writeFileSync(join(out, "deck.html"), buildHtml(deck, out));
  printPdf(join(out, "deck.html"), join(out, "deck.pdf"));
  console.log(`${slides.length} slides -> ${join(out, "deck.pdf")}`);
} finally {
  paper.kill();
}
