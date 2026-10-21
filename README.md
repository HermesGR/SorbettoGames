# SorbettoGames

SorbettoGames is a Kodi add-on project for browsing and installing individual PlayStation game files that the repository owner is authorised to distribute. It is designed for Kodi 21 (Python 3) and uses RetroArch with the PCSX-ReARMed core to launch compatible games.

> **Status:** Version 1.0.0 package prepared for testing. Installation, game downloads, and launching must be tested in the target Kodi/RetroArch setup before this version is considered production-ready.

## Features

- Reads game assets from the latest GitHub Release in `HermesGR/SorbettoGames`.
- Lists each supported game asset separately.
- Downloads only the game selected by the user, rather than the entire collection.
- Supports an optional `sorbetto-catalog.json` manifest for custom titles and descriptions.
- Provides local game management and a launch path through RetroArch / PCSX-ReARMed.

## Requirements

- Kodi 21 or another compatible Kodi version using Python 3.
- RetroArch installed separately.
- The PCSX-ReARMed core installed and compatible with the device.
- A supported game image that the user is authorised to use.

The add-on does **not** include commercial game ROMs or BIOS files.

## Install the Kodi add-on

1. Download `repository.sorbetto.games-1.0.0.zip` from the project’s release/package files.
2. In Kodi, open **Add-ons → Install from zip file** and select the repository ZIP.
3. Open the SorbettoGames repository and install **SorbettoGames**.
4. Open the add-on settings and configure RetroArch and the PCSX-ReARMed core as required by your device.

If installing the add-on directly for testing, use `plugin.program.sorbetto.games-1.0.0.zip` with Kodi’s **Install from zip file** option.

## Publish games in a GitHub Release

Create a Release in this repository:

<https://github.com/HermesGR/SorbettoGames/releases>

Upload **one separate ZIP asset per game**. For example:

- `Example_Game_One.zip`
- `Example_Game_Two.zip`

Each game ZIP should contain only that game's supported image files. For multi-file disc images, include the `.cue` file and its matching `.bin` file(s), or use a supported single-file format such as `.chd` or `.pbp`. Keep the game files at the ZIP root or inside one folder. Use clear, unique ZIP filenames.

The add-on is intended to list supported ZIP assets from the latest Release and download only the selected asset. Do not place the add-on or repository installation ZIPs in the game list as game assets. Because this behaviour has not yet been verified against every Release layout, test with one small, authorised game asset first.

### Optional game metadata

You may attach a file named `sorbetto-catalog.json` to the same Release to define custom titles and descriptions. Example:

```json
{
  "schema": 1,
  "games": [
    {
      "asset": "Example_Game_One.zip",
      "id": "example-game-one",
      "title": "Example Game One",
      "description": "Example description"
    }
  ]
}
```

The `asset` value must match the corresponding Release asset filename exactly. Without a manifest, the asset filename is intended to be used as the displayed title.

## GitHub Pages repository feed

The Kodi repository feed is configured to use:

- <https://hermesgr.github.io/SorbettoGames/addons.xml>
- <https://hermesgr.github.io/SorbettoGames/addons.xml.md5>

When publishing the repository feed, upload the **contents** of the generated `github-pages` folder to the root of the GitHub Pages publishing location—not the folder itself as an extra nested directory. Ensure that `addons.xml`, `addons.xml.md5`, and the matching add-on ZIP files are reachable at the URLs above.

## RetroArch setup

### Windows

In the add-on settings, set the path to `retroarch.exe` and the installed PCSX-ReARMed core DLL. Confirm the paths on the machine where Kodi runs.

### Android TV / NVIDIA Shield

Install RetroArch and the PCSX-ReARMed core separately. If needed, set the correct RetroArch package name in the add-on settings. Android launch and file-access behaviour varies by RetroArch build and Kodi version; verify it on the actual target device before distributing the add-on.

## Troubleshooting

- **No games listed:** confirm that the latest GitHub Release is public and contains individual game ZIP assets.
- **A game does not download:** check the asset filename, public accessibility, network connection, and available storage.
- **A game downloads but does not launch:** check that the archive contains a supported image, that any `.cue` references match the included filenames, and that RetroArch and PCSX-ReARMed are installed and configured correctly.
- **Repository does not update:** verify the GitHub Pages publishing root, `addons.xml`, its MD5 checksum, and the asset ZIP URLs.

## Licence and distribution

Only upload game files and other assets that you own or are authorised to distribute. The add-on does not provide ROMs or BIOS files. Check the licences and permissions applicable to every asset you publish.

## Project links

- Repository: <https://github.com/HermesGR/SorbettoGames>
- Releases: <https://github.com/HermesGR/SorbettoGames/releases>
- Kodi repository feed: <https://hermesgr.github.io/SorbettoGames/addons.xml>
