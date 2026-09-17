#!/usr/bin/env python3
"""Run every editorial-web-craft checker on one or more files and merge the results.

Usage:  audit.py page.html [styles.css ...] [--json] [--strict] [--allow-cdn] [--allow-fonts]

Discovers the sibling skills' check_*.py scripts relative to this file
(../../<skill>/scripts/check_*.py), so it works from any install that keeps the
set together (plugin, npx skills, symlinks). If a checker is missing — e.g. a
single .skill uploaded on its own — it is reported as UNAVAILABLE, not skipped
silently.

Exit 1 if any checker reports a FAIL. --json prints a machine-readable summary.
"""
import json
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SKILLS = HERE.parent.parent            # …/skills/

CHECKERS = [
    ("single-file", "encapsulated-mockup-builder/scripts/check_single_file.py", "html", ["--strict", "--allow-cdn", "--allow-fonts"]),
    ("layers",      "cascading-specificity-guard/scripts/check_layers.py",      "any",  []),
    ("motion",      "reduced-motion-enforcer/scripts/check_motion.py",          "any",  []),
    ("semantics",   "html5-native-fallback/scripts/check_semantics.py",         "html", []),
    ("ink",         "accessible-ink-scale/scripts/check_ink.py",                "any",  []),
    ("cls",         "cls-dimension-anchor/scripts/check_cls.py",                "any",  []),
    ("z-index",     "z-index-coordinate-matrix/scripts/check_zindex.py",        "any",  []),
]


def run(label, script, files, passthrough):
    path = SKILLS / script
    if not path.exists():
        return {"checker": label, "status": "UNAVAILABLE", "fails": [], "warns": [], "note": f"{script} not installed"}
    cmd = [sys.executable, str(path), *files, *passthrough]
    p = subprocess.run(cmd, capture_output=True, text=True)
    out = p.stdout + p.stderr
    fails = [l.strip() for l in out.splitlines() if re.match(r"\s*FAIL", l)]
    warns = [l.strip() for l in out.splitlines() if re.match(r"\s*WARN", l)]
    if "Traceback" in out:
        return {"checker": label, "status": "ERROR", "fails": [], "warns": [], "note": out.strip().splitlines()[-1]}
    return {"checker": label, "status": "FAIL" if fails else ("WARN" if warns else "OK"), "fails": fails, "warns": warns}


def main() -> None:
    args = sys.argv[1:]
    as_json = "--json" in args
    flags = [a for a in args if a.startswith("--") and a != "--json"]
    files = [a for a in args if not a.startswith("--")]
    if not files:
        sys.exit(__doc__)
    html = [f for f in files if f.lower().endswith((".html", ".htm"))]
    results = []
    for label, script, kind, accepts in CHECKERS:
        target = html if kind == "html" else files
        if not target:
            continue
        results.append(run(label, script, target, [f for f in flags if f in accepts]))

    if as_json:
        print(json.dumps({"files": files, "results": results}, indent=2))
    else:
        width = max(len(r["checker"]) for r in results)
        for r in results:
            print(f"{r['checker']:<{width}}  {r['status']}" + (f"  ({r['note']})" if r.get("note") else ""))
            for f in r["fails"]:
                print(f"{'':<{width}}    {f}")
            for w in r["warns"]:
                print(f"{'':<{width}}    {w}")
        n_fail = sum(len(r["fails"]) for r in results)
        n_warn = sum(len(r["warns"]) for r in results)
        unavailable = [r["checker"] for r in results if r["status"] == "UNAVAILABLE"]
        print(f"\n{n_fail} FAIL, {n_warn} WARN across {len(results)} checkers on {len(files)} file(s)"
              + (f"; unavailable: {', '.join(unavailable)}" if unavailable else ""))
    sys.exit(1 if any(r["fails"] or r["status"] == "ERROR" for r in results) else 0)


if __name__ == "__main__":
    main()
