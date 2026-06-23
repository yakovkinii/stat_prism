# Installation

StatPrism is a desktop application for Windows.

## Install from a release

1. Go to the project's [**Releases** page on GitHub](https://github.com/yakovkinii/stat_prism/releases).
2. Download the latest StatPrism build for Windows.
3. Unzip it to a folder you can write to (for example, your Desktop or Documents).
4. Run the StatPrism executable to launch the app.

No separate Python installation is required for the packaged build — everything needed is
included.

```{tip}
You can optionally associate `.sp` project files with StatPrism so that double-clicking a
saved project opens it directly.
```

## Running from source (for developers)

If you are working from the source repository instead of a packaged release, launch the
app with the bundled environment using the provided run script (`_RUN.bat`). See the
repository's `README` for the developer setup.

## Updating

To update, download the newer release and replace your existing copy. Your saved `.sp`
project files are independent of the application folder and are not affected by updating.

## What you'll need

- A Windows PC.
- Your data as a spreadsheet — typically a `.xlsx` or `.csv` exported from a survey tool
  such as Google Forms. See {doc}`importing-data`.
