# Release checklist

The version lives in **one place** — `src/about.py`. The docs read it dynamically
(`docs/conf.py` parses it; `citing.md` uses the `{{ release }}` substitution), and
`tools/release.py` syncs the only two files that hardcode it (`README.md`, `CITATION.cff`).
**Do not edit version numbers by hand.**

1. **Bump + format + sync** — pick exactly one of `patch` / `minor` / `major`:
   ```
   _RELEASE.bat patch          rem 1.0.2 -> 1.0.3
   _RELEASE.bat minor          rem 1.0.2 -> 1.1.0
   _RELEASE.bat major          rem 1.0.2 -> 2.0.0
   _RELEASE.bat patch --check  rem dry run, writes nothing
   ```
   Every run **formats the code** (isort + black) and **lints** it (flake8) before bumping
   `src/about.py`, `README.md`, `CITATION.cff` (version + date) and adding a `RELEASE_NOTES.md`
   stub. black/isort config lives in `pyproject.toml`; flake8 config in `.flake8`; the dev
   tools are pinned in `requirements-dev.txt` and installed into `venv_39` automatically.
   (Pass `--no-format` to skip formatting for a quick hotfix.)

2. **Fill in** `RELEASE_NOTES.md` for the new version.

3. **Run the pre-release checks** (each runs in the right venv):
   ```
   _RELEASE.bat <part> --test    rem pytest (snapshot suite)
   _RELEASE.bat <part> --docs    rem build the user guide
   _RELEASE.bat <part> --build   rem nuitka standalone exe
   ```
   (Snapshot tests render HTML; review/approve changes with `_TEST_SUITE.bat` first. The
   suite always renders in the light UI theme, English, and the default plot theme.)

4. **Commit, tag, push:**
   ```
   git add -A && git commit -m "Release <version>"
   git tag v<version> && git push && git push --tags
   ```

5. **Create the GitHub release** for `v<version>` and attach the built exe.
