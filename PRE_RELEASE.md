# Release checklist

Assumes the dev environment (`venv_39`) is checked out and populated.

1. Check (dry run, writes nothing)
   ```bash
   ./venv_39/Scripts/python.exe tools/release.py patch --check
   ```
2. Bump version and run formatters (pick one)
   ```bash
   ./venv_39/Scripts/python.exe tools/release.py patch
   ```
   ```bash
   ./venv_39/Scripts/python.exe tools/release.py minor
   ```
   ```bash
   ./venv_39/Scripts/python.exe tools/release.py major
   ```
3. Review the snapshot test suite (opens the review GUI)
   ```bash
   ./venv_39/Scripts/pythonw.exe tools/snapshot_review.py
   ```
4. **Fill in** `RELEASE_NOTES.md` for the new version.
