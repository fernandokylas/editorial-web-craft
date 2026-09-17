#!/usr/bin/env python3
"""Package each skills/<name> as <name>.skill (a zip whose root is the skill folder — the format
Claude.ai accepts as a custom skill upload), plus one bundle of the whole set.

Usage:  package_skills.py [out-dir]     (default: dist)
"""
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILLS = ROOT / "skills"
EXCLUDE = {".DS_Store", "__pycache__", ".pyc"}


def wanted(p: Path) -> bool:
    return not any(part in EXCLUDE or part.endswith(".pyc") for part in p.parts)


def main() -> None:
    out = Path(sys.argv[1] if len(sys.argv) > 1 else "dist")
    out.mkdir(parents=True, exist_ok=True)
    bundle = zipfile.ZipFile(out / "editorial-web-craft-skills.zip", "w", zipfile.ZIP_DEFLATED)
    n = 0
    for skill in sorted(p for p in SKILLS.iterdir() if p.is_dir() and (p / "SKILL.md").exists()):
        with zipfile.ZipFile(out / f"{skill.name}.skill", "w", zipfile.ZIP_DEFLATED) as z:
            for f in sorted(skill.rglob("*")):
                if f.is_file() and wanted(f.relative_to(skill)):
                    arc = f"{skill.name}/{f.relative_to(skill)}"
                    z.write(f, arc)
                    bundle.write(f, arc)
        n += 1
        print(f"{skill.name}.skill")
    bundle.close()
    print(f"\n{n} skills → {out}/  (+ editorial-web-craft-skills.zip)")


if __name__ == "__main__":
    main()
