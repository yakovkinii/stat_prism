# Release checklist

1. Check 
   ```bash
   ./_RELEASE.bat patch --check
   ```
2. Bump version and run formatters
   ```bash
   ./_RELEASE.bat patch
   ```
   ```bash
   ./_RELEASE.bat minor
      ```
   ```bash
   ./_RELEASE.bat major
   ```
3. **Fill in** `RELEASE_NOTES.md` for the new version.
