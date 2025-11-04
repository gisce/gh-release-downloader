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

**Auto-update is enabled by default.** The tool will automatically check for and install updates before running.

To disable automatic updates, use the `--no-auto-update` flag:

```bash
gh-release-downloader <owner/repo> --no-auto-update
```

When auto-update is enabled, the tool will:
1. Check if a newer version is available
2. Download and install the updated binary (only for PyInstaller binary installations)
3. Re-execute with the same arguments

**Note:** Auto-update only works with binary installations created via PyInstaller. For Python script installations, update manually with:
```bash
pip install --upgrade gh-release-downloader
```

## Slack Configuration

To receive notifications on Slack, you will need to set up a webhook in Slack and pass it as the `--webhook-url` parameter. Notifications will include details of the downloaded release and the link provided in `--url-client`.

### Markdown to Slack Format Transformer

The project includes a `markdown_to_slack_format()` function that automatically converts GitHub markdown to Slack-compatible format. This function is used internally for Slack notifications but can also be imported and used in other scripts or bots.

**Features:**
- Converts headers (`#` -> uppercase/formatted text)
- Converts links `[text](url)` -> `<url|text>`
- Converts bold `**text**` -> `*text*` (Slack format)
- Converts italic `*text*` or `_text_` -> `_text_` (Slack format)
- Converts list markers (`-`, `*`, `+`) -> bullet points (`•`)
- Preserves code blocks and quotes
- Handles nested formatting correctly

**Usage Example:**

```python
from gh_release_downloader import markdown_to_slack_format

# GitHub markdown
markdown_text = """## Release v1.0.0

- Added **new feature** with [documentation](https://example.com)
- Fixed _critical bug_

```bash
pip install package
```
"""

# Convert to Slack format
slack_text = markdown_to_slack_format(markdown_text)
# Result:
# *Release v1.0.0*
# 
# • Added *new feature* with <https://example.com|documentation>
# • Fixed _critical bug_
# 
# ```bash
# pip install package
# ```
```

See `example_usage.py` for more examples of using this function in your own scripts or bots.

## Contributions

Contributions to this project are welcome. Please open an issue or submit a Pull Request with your suggestions and improvements.

## License

[MIT](LICENSE)
