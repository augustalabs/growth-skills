#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Gate between the steps of a deck run: refuse to continue while plan.json has a gap.

    uv run plan_check.py <run>/plan.json --stage decisions|write|build

decisions  every mapping decision answered with a reason; the portfolio is confirmed;
           every slide known to the plan
write      + every slide that runs has content (FIXED boilerplate excepted); no leftover
           template tokens. Figures in written content are listed as warnings to review
           (guideline: keep impact qualitative), not as failures.
build      + every slide that runs was built (artboard id recorded)

Exit 0 when the plan passes, 1 with the list of gaps when it doesn't.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

TOKENS = ["ACME", "<Fund>", "<Client>", "[Industry Group]", "<Industry Group>", "Month YYYY",
          "[use case TBD]", "TBD", "Lorem"]
# A figure in authored text: money, percentages, multiples, "100M"-style amounts.
# Case-card fields are copied from the case library and are exempt.
FIGURE = re.compile(r"[€$£]\s?\d[\d.,]*\s?(?:M|bn|B|k|mil|milhões|million|billion)?"
                    r"|\d[\d.,]*\s?(?:%|x\b|×|M\b|bn\b|B\b|k\b|mil\b|milhões|million|billion)",
                    re.IGNORECASE)
CASE_KEYS = {"case", "case_card", "card"}


def walk(v, path=""):
    """Yield (path, text) for every string in a nested content value."""
    if isinstance(v, str):
        yield path, v
    elif isinstance(v, dict):
        for k, x in v.items():
            yield from walk(x, f"{path}.{k}" if path else k)
    elif isinstance(v, list):
        for i, x in enumerate(v):
            yield from walk(x, f"{path}[{i}]")


def check(plan: dict, stage: str) -> tuple[list[str], list[str]]:
    gaps: list[str] = []
    warnings: list[str] = []
    req = plan.get("request", {})
    for k in ("row", "fund", "language", "date"):
        if not req.get(k):
            gaps.append(f"request.{k} is empty")

    slides = plan.get("slides") or []
    if not slides:
        gaps.append("no slides in the plan")

    for d in plan.get("decisions") or []:
        if not str(d.get("answer", "")).strip():
            gaps.append(f"decision unanswered: [{d.get('group')}] {d.get('question')}")
        elif not str(d.get("reason", "")).strip():
            gaps.append(f"decision without a reason: [{d.get('group')}] {d.get('question')}")

    confirmed = {p.get("company", "").strip().lower() for p in (plan.get("research", {}).get("portfolio") or [])}
    for s in slides:
        company = (s.get("company") or "").strip()
        if company and s.get("runs") and company.lower() not in confirmed:
            gaps.append(f"{s.get('name')}: company '{company}' is not on research's confirmed-current list")

    if stage in ("write", "build"):
        for s in slides:
            if not s.get("runs"):
                continue
            name = s.get("name") + (f" · {s['instance']}" if s.get("instance") else "")
            if s.get("class") != "FIXED" and not s.get("content"):
                gaps.append(f"{name}: no content")
            for path, text in walk(s.get("content") or {}):
                for t in TOKENS:
                    if t in text:
                        gaps.append(f"{name}: leftover token '{t}' in {path}")
                if path.split(".")[0] in CASE_KEYS:
                    continue
                for m in FIGURE.finditer(text):
                    warnings.append(f"{name}: figure '{m.group(0)}' in {path}: fine if it's a sourced fact, "
                                    "otherwise say the impact qualitatively")
            if s.get("case") is None and "deep dive" in (s.get("name") or "").lower():
                gaps.append(f"{name}: no case study picked")

    if stage == "build":
        for s in slides:
            if s.get("runs") and not s.get("built"):
                gaps.append(f"{s.get('name')}{' · ' + s['instance'] if s.get('instance') else ''}: not built")
    return gaps, warnings


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("plan")
    ap.add_argument("--stage", choices=["decisions", "write", "build"], required=True)
    a = ap.parse_args()
    plan = json.loads(Path(a.plan).read_text())
    gaps, warnings = check(plan, a.stage)
    if warnings:
        print(f"REVIEW ({len(warnings)}):")
        for w in warnings:
            print(" ~", w)
    if gaps:
        print(f"PLAN CHECK FAILED ({a.stage}): {len(gaps)} gap(s)")
        for g in gaps:
            print(" -", g)
        sys.exit(1)
    print(f"PLAN CHECK PASSED ({a.stage})")


if __name__ == "__main__":
    main()
