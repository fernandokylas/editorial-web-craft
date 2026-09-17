#!/usr/bin/env python3
"""PostToolUse hook: audit a just-written page, but only if it belongs to this set.

Reads the tool event from stdin, exits 0 silently unless the written file is
.html/.css AND carries the set's layer marker
(`@layer base, layout, components, utilities`). Then runs web-craft's audit.py
and, on any FAIL, exits 2 with the FAIL lines on stderr so Claude sees them.
The marker gate keeps the hook quiet in projects that don't use the set.
"""
import json
import os
import re
import subprocess
import sys
from pathlib import Path

MARKER = re.compile(r"@layer\s+base\s*,\s*layout\s*,\s*components\s*,\s*utilities\s*;")


def main() -> None:
    try:
        event = json.load(sys.stdin)
    except Exception:
        return
    path = (event.get("tool_input") or {}).get("file_path") or ""
    if not path.lower().endswith((".html", ".htm", ".css")):
        return
    p = Path(path)
    if not p.is_file():
        return
    try:
        text = p.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return
    if not MARKER.search(text):
        return
    root = Path(os.environ.get("CLAUDE_PLUGIN_ROOT", Path(__file__).resolve().parent.parent))
    audit = root / "skills" / "web-craft" / "scripts" / "audit.py"
    if not audit.exists():
        return
    r = subprocess.run([sys.executable, str(audit), str(p), "--allow-cdn", "--allow-fonts"], capture_output=True, text=True)
    fails = [l for l in r.stdout.splitlines() if "FAIL" in l]
    if r.returncode != 0 and fails:
        sys.stderr.write(f"editorial-web-craft audit — {p.name}:\n" + "\n".join(fails) + "\n")
        sys.exit(2)
    print(f"editorial-web-craft audit — {p.name}: {r.stdout.strip().splitlines()[-1]}")


if __name__ == "__main__":
    main()
