# Packaging & Windows CI

The GitHub Actions workflow [`.github/workflows/build-windows.yml`](../.github/workflows/build-windows.yml)
builds a **standalone** StatPrism with Nuitka and wraps it in an **Inno Setup** installer.

## How it runs

- **Tag push** `vX.Y.Z` → builds and **attaches the installer to that tag's GitHub Release**.
- **Manual** ("Actions → Build Windows installer → Run workflow") → builds and uploads the
  installer as a downloadable **workflow artifact** (no release needed).

The app version is read automatically from `src/about.py`, so a release is just:

```
python tools/release.py minor      # bumps src/about.py, formats, syncs README/CITATION
git commit -am "1.2.0"
git tag v1.2.0
git push && git push --tags        # the tag push triggers the build
```

## One-time configuration (required)

**Installer `AppId` GUID.** In `packaging/installer.iss` replace the placeholder
`AppId={{B7F2B5B0-...STATPRISM0001}}` with a real GUID **once** and never change it — Windows
uses it to recognise upgrades. Generate one with any UUID tool or the Inno Setup IDE
(Tools → Generate GUID).

That is the only manual step: all runtime dependencies (including `yatools`) come from
`requirements.txt` via PyPI.

## What the workflow does

1. Reads the version from `src/about.py`.
2. Installs Python 3.9 + `requirements.txt` + Nuitka.
3. `python -m nuitka --assume-yes-for-downloads launcher.py` — options come from the
   `# nuitka-project:` directives already in `launcher.py`; output lands in
   `build/nuitka/launcher.dist/` with the main binary renamed `StatPrism.exe`.
4. Downloads `vc_redist.x64.exe` (bundled into the installer as a safety net — the standalone
   folder normally already carries the needed runtime DLLs; the installer only runs the redist if
   the machine lacks the VC++ 2015-2022 x64 runtime).
5. Installs Inno Setup via Chocolatey and compiles `packaging/installer.iss`.
6. Uploads `packaging/Output/StatPrism-<version>-setup.exe`.

## Building the installer locally

```
venv_39\Scripts\python.exe -m nuitka launcher.py
:: download vc_redist.x64.exe into packaging\ (or delete that [Files]/[Run]/Check line)
"C:\Program Files (x86)\Inno Setup 6\ISCC.exe" /DAppVersion=1.1.0 packaging\installer.iss
```

## Notes / gotchas

- **Nuitka + QtWebEngine.** StatPrism uses `QWebEngineView`; the `pyside6` Nuitka plugin bundles
  QtWebEngine, but it is large and occasionally needs extra Qt plugins. If the packaged app can't
  show the results view, that is the first place to look.
- **Console window.** `launcher.py` currently forces a console (`--windows-console-mode=force`).
  For a release build you may want `disable` (no console) — change that directive.
- **Build time.** A cold Nuitka standalone build of a Qt app is slow (~15-40 min on the runner).
  Consider adding Nuitka's caching (`Nuitka/Nuitka-Action`, or cache `~/.cache/Nuitka`) later.
- **Signing.** The installer and exe are unsigned, so SmartScreen will warn users. Add an
  Authenticode signing step (certificate in a secret) when you have a cert.
