#!/usr/bin/env python3
"""Collect open action items from meeting-notes markdown files.

Usage: python3 extract_action_items.py notes/*.md
Prints every unchecked "- [ ] ..." line with the file it came from, so
follow-ups scattered across many meetings end up in one list.
"""
import re
import sys

OPEN_ITEM = re.compile(r"^\s*-\s*\[ \]\s*(.+)$")


def main(paths):
    found = 0
    for path in paths:
        with open(path, encoding="utf-8") as f:
            for line in f:
                match = OPEN_ITEM.match(line)
                if match:
                    print(f"{path}: {match.group(1).strip()}")
                    found += 1
    print(f"\n{found} open action item(s)", file=sys.stderr)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit("usage: extract_action_items.py <notes.md> [notes2.md ...]")
    main(sys.argv[1:])
