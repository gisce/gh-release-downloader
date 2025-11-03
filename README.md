# GitHub Release Asset Downloader

This project provides a Python script, `gh-release-downloader.py`, for automating the download of release assets from a GitHub repository. It supports unzipping `.zip` files, saves a record of the last downloaded release to avoid redundant downloads, and can send notifications to Slack.

## Features

- Downloads assets from GitHub releases.
- Option to include only pre-releases or filter by a specific version prefix.
- Option to include pre-releases types (eg. alpha, beta, rc, etc.)
- Automatically unzips `.zip` files.
- Saves a record of the last downloaded release.
- Sends notifications to Slack upon successful download.
- Auto-update functionality to keep gh-release-downloader up to date.

## Requirements

- Python 3.x
- Python libraries: `requests`, `click`, `json`, `zipfile`
- A personal GitHub access token with appropriate permissions.
- (Optional) A Slack webhook for sending notifications.

## Installation

1. Clone this repository or download the files directly.
2. Install the required dependencies:
   ```bash
   pip install requests click
   ```
3. Set up the required environment variables:
   - `GITHUB_TOKEN`: Your GitHub personal access token.

## Usage

Run the script with Python from the command line. Here is an example of how to use it:

```bash
python gh-release-downloader.py <owner/repo> --pre-release --version-prefix "v1" --webhook-url "YOUR_SLACK_WEBHOOK_URL" --url-client "YOUR_CLIENT_URL" --output-dir "download_directory"
```

Replace `<owner/repo>` with the owner and the name of the GitHub repository from which you want to download assets.

### Auto-Update

To enable automatic updates of gh-release-downloader itself, use the `--auto-update` flag:

```bash
gh-release-downloader <owner/repo> --auto-update
```

When enabled, the tool will:
1. Check if a newer version is available
2. Download and install the updated binary (only for PyInstaller binary installations)
3. Re-execute with the same arguments

**Note:** Auto-update only works with binary installations created via PyInstaller. For Python script installations, update manually with:
```bash
pip install --upgrade gh-release-downloader
```

## Slack Configuration

To receive notifications on Slack, you will need to set up a webhook in Slack and pass it as the `--webhook-url` parameter. Notifications will include details of the downloaded release and the link provided in `--url-client`.

## Contributions

Contributions to this project are welcome. Please open an issue or submit a Pull Request with your suggestions and improvements.

## License

[MIT](LICENSE)
