#  Copyright (c) 2023 StatPrism Team. All rights reserved.
"""StatPrism release helper.

`src/about.py` is the single source of truth for the version. The docs read it
dynamically (docs/conf.py parses it; citing.md uses the {{ release }} substitution), so
the only files that still hardcode the version are README.md and CITATION.cff. This script
bumps about.py and syncs those, so a release needs no manual version edits.

Every release also runs the formatters/linter (black, isort, flake8) so the released
commit is clean. black + isort are configured in pyproject.toml; flake8 in .flake8.

Usage (run with the app interpreter, e.g. via _RELEASE.bat):

    python tools/release.py patch   # 1.0.2 -> 1.0.3
    python tools/release.py minor   # 1.0.2 -> 1.1.0
    python tools/release.py major   # 1.0.2 -> 2.0.0

    python tools/release.py patch --check   # dry run: show changes, write nothing
    python tools/release.py patch --no-format   # skip the formatters/linter

Optional pre-release steps (off by default; each runs in the matching venv):

    --test    run the test suite (venv_39 python -m pytest -q)
    --docs    build the user guide (venv_docs, like _BUILD_DOCS.bat)
    --build   build the standalone exe (venv_39 python -m nuitka launcher.py)

After it succeeds it prints the remaining manual git / GitHub-release steps.
"""

from __future__ import annotations

import argparse
import datetime as _dt
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ABOUT = ROOT / "src" / "about.py"
README = ROOT / "README.md"
CITATION = ROOT / "CITATION.cff"
RELEASE_NOTES = ROOT / "RELEASE_NOTES.md"
DEV_REQUIREMENTS = ROOT / "requirements-dev.txt"

# What black / isort / flake8 are pointed at (flake8 further trims via .flake8 exclude).
FORMAT_TARGETS = ["src", "tools", "tests", "launcher.py"]

_VERSION_RE = re.compile(r'(version\s*=\s*")([^"]+)(")')
_SEMVER_RE = re.compile(r"^\d+\.\d+\.\d+$")


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _write(path: Path, text: str, dry_run: bool) -> None:
    if dry_run:
        print(f"  [dry-run] would write {path.relative_to(ROOT)}")
    else:
        path.write_text(text, encoding="utf-8")
        print(f"  updated {path.relative_to(ROOT)}")


def current_version() -> str:
    match = _VERSION_RE.search(_read(ABOUT))
    if not match:
        sys.exit(f"Could not find a version in {ABOUT}")
    return match.group(2)


def bump(version: str, part: str) -> str:
    if not _SEMVER_RE.match(version):
        sys.exit(f"Current version '{version}' is not X.Y.Z; fix src/about.py first.")
    major, minor, patch = (int(x) for x in version.split("."))
    if part == "major":
        major, minor, patch = major + 1, 0, 0
    elif part == "minor":
        minor, patch = minor + 1, 0
    else:  # patch
        patch += 1
    return f"{major}.{minor}.{patch}"


def set_about(new: str, dry_run: bool) -> None:
    text = _read(ABOUT)
    new_text, n = _VERSION_RE.subn(rf'\g<1>{new}\g<3>', text, count=1)
    if n != 1:
        sys.exit(f"Could not update the version in {ABOUT}")
    _write(ABOUT, new_text, dry_run)


def sync_readme(new: str, dry_run: bool) -> None:
    text = _read(README)
    new_text, n = re.subn(r"\(Version\s+[^)]+\)", f"(Version {new})", text)
    if n == 0:
        print(f"  WARNING: no '(Version ...)' found in {README.name}; skipped")
        return
    _write(README, new_text, dry_run)


def sync_citation(new: str, today: str, dry_run: bool) -> None:
    text = _read(CITATION)
    text, n = re.subn(r"(?m)^version:.*$", f"version: {new}", text)
    if n == 0:
        print(f"  WARNING: no 'version:' line in {CITATION.name}; skipped")
        return
    if re.search(r"(?m)^date-released:", text):
        text = re.sub(r"(?m)^date-released:.*$", f"date-released: {today}", text)
    else:
        # Insert right after the version line so the file stays tidy.
        text = re.sub(r"(?m)^(version:.*)$", rf"\1\ndate-released: {today}", text, count=1)
    _write(CITATION, text, dry_run)


def add_release_note_stub(new: str, dry_run: bool) -> None:
    """Insert a dated heading for this version after the title, unless it already exists."""
    if not RELEASE_NOTES.exists():
        return
    text = _read(RELEASE_NOTES)
    if f"### StatPrism {new} " in text:
        print(f"  {RELEASE_NOTES.name}: heading for {new} already present; skipped")
        return
    now = _dt.date.today()
    heading = f"### StatPrism {new} ({now.day} {now:%b %Y})\n\n* TODO: summarise changes.\n\n"
    anchor = "# StatPrism Release Notes\n"
    if anchor in text:
        text = text.replace(anchor, anchor + "\n" + heading, 1)
    else:
        text = heading + text
    _write(RELEASE_NOTES, text, dry_run)


def venv_python(venv: str) -> Path:
    exe = ROOT / venv / "Scripts" / "python.exe"
    if not exe.exists():
        sys.exit(f"{exe} not found. Create the environment first (e.g. _CREATE_ENV.bat).")
    return exe


def run_step(label: str, args: list, check: bool = True) -> int:
    print(f"\n=== {label} ===\n  $ {' '.join(str(a) for a in args)}")
    result = subprocess.run(args, cwd=str(ROOT))
    if check and result.returncode != 0:
        sys.exit(f"{label} failed (exit {result.returncode}). Fix it before releasing.")
    return result.returncode


def run_formatters(dry_run: bool) -> None:
    """Install the dev tools (into venv_39) then run isort, black and flake8.

    isort/black auto-fix the code (or only report in --check mode); flake8 only reports.
    An isort/black failure aborts the release; flake8 findings are surfaced as a loud
    warning but do not block, so legacy lint debt cannot wedge a release."""
    py = venv_python("venv_39")
    targets = [t for t in FORMAT_TARGETS if (ROOT / t).exists()]

    if DEV_REQUIREMENTS.exists():
        run_step(
            "Install dev tools",
            [py, "-m", "pip", "install", "-r", str(DEV_REQUIREMENTS), "-q", "--disable-pip-version-check"],
        )

    isort_args = [py, "-m", "isort", *targets] + (["--check-only", "--diff"] if dry_run else [])
    run_step("isort" + (" (check)" if dry_run else ""), isort_args)

    black_args = [py, "-m", "black", *targets] + (["--check", "--diff"] if dry_run else [])
    run_step("black" + (" (check)" if dry_run else ""), black_args)

    code = run_step("flake8", [py, "-m", "flake8", *targets], check=False)
    if code != 0:
        print("\n  !! flake8 reported issues above. They do NOT block the release, but")
        print("     please review and fix them before tagging.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Bump the StatPrism version, format the code, and sync static files.")
    parser.add_argument("part", choices=["patch", "minor", "major"], help="which version part to bump")
    parser.add_argument("--check", action="store_true", help="dry run: report changes, write nothing")
    parser.add_argument("--no-format", action="store_true", help="skip the isort/black/flake8 step")
    parser.add_argument("--no-notes", action="store_true", help="do not add a RELEASE_NOTES stub")
    parser.add_argument("--test", action="store_true", help="run the test suite (venv_39)")
    parser.add_argument("--docs", action="store_true", help="build the user guide (venv_docs)")
    parser.add_argument("--build", action="store_true", help="build the standalone exe (nuitka)")
    args = parser.parse_args()

    old = current_version()
    new = bump(old, args.part)

    today = _dt.date.today().isoformat()
    print(f"Version: {old} -> {new}  ({args.part}){'   (dry run)' if args.check else ''}")

    if not args.no_format:
        run_formatters(args.check)

    set_about(new, args.check)
    sync_readme(new, args.check)
    sync_citation(new, today, args.check)
    if not args.no_notes:
        add_release_note_stub(new, args.check)

    if args.test:
        run_step("Test suite", [venv_python("venv_39"), "-m", "pytest", "-q"])
    if args.docs:
        run_step("Docs build", [venv_python("venv_docs"), "-m", "sphinx", "-b", "html", "docs", "docs/_build/html"])
    if args.build:
        run_step("Nuitka build", [venv_python("venv_39"), "-m", "nuitka", "launcher.py"])

    print("\nNext (manual) steps:")
    print(f"  1. Review the diffs and fill in RELEASE_NOTES.md for {new}.")
    if not (args.test and args.docs):
        print("  2. Run checks if you skipped them: --test / --docs / --build run the heavier steps.")
    print(f"  3. git add -A && git commit -m \"Release {new}\"")
    print(f"  4. git tag v{new} && git push && git push --tags")
    print(f"  5. Create the GitHub release for v{new} and attach the built exe.")


if __name__ == "__main__":
    main()
