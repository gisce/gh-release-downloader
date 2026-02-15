# GitHub Release Asset Downloader

A powerful command-line tool to automate the download and deployment of release assets from GitHub repositories. Perfect for keeping your servers updated with the latest releases, managing multiple deployments, and integrating with CI/CD pipelines.

## What is gh-release-downloader?

`gh-release-downloader` is a tool that monitors GitHub repositories for new releases and automatically downloads their assets. It's particularly useful for:

- **Automated deployments**: Keep your production servers updated with the latest releases
- **Release monitoring**: Track and download specific versions or pre-releases
- **Team notifications**: Send Slack notifications when new releases are deployed
- **Version management**: Filter releases by version prefix or pre-release type
- **Self-updating**: The tool can update itself automatically to the latest version

## How Does It Work?

1. **Connects to GitHub**: Uses the GitHub API to fetch release information from a specified repository
2. **Filters releases**: Applies your criteria (version prefix, pre-release type, etc.) to find the target release
3. **Checks for updates**: Compares with the last downloaded release to avoid redundant downloads
4. **Downloads assets**: Retrieves release assets (binaries, packages, etc.)
5. **Processes files**: Automatically extracts `.zip` files
6. **Notifies your team**: Sends a Slack notification with release details (optional)
7. **Keeps records**: Saves information about the last downloaded release for future comparisons

## Features

- ✅ Downloads assets from GitHub releases (latest or specific versions)
- ✅ Support for pre-releases and custom version filtering
- ✅ Pre-release type filtering (alpha, beta, rc, etc.)
- ✅ Automatically extracts `.zip` files
- ✅ Tracks last downloaded release to avoid redundant downloads
- ✅ Slack notifications with optional release notes
- ✅ Self-updating capability (binary installations only)
- ✅ Cross-platform support (Linux, macOS, Windows)

## Requirements

- Python 3.6 or higher (for script installation)
- A GitHub personal access token with appropriate permissions
- (Optional) A Slack webhook URL for notifications

## Installation

There are two ways to install `gh-release-downloader`:

### Option 1: Pre-built Static Binary (Recommended for Servers)

The easiest way to install on a server is to download the pre-built static binary from the [latest release](https://github.com/gisce/gh-release-downloader/releases/latest):

```bash
# Download the latest binary
curl -L -o gh-release-downloader https://github.com/gisce/gh-release-downloader/releases/latest/download/gh-release-downloader

# Make it executable
chmod +x gh-release-downloader

# Move to a directory in your PATH (optional)
sudo mv gh-release-downloader /usr/local/bin/

# Test the installation
gh-release-downloader --version
```

**Benefits of the static binary:**
- ✅ No Python installation required
- ✅ No dependency management
- ✅ Self-contained and ready to use
- ✅ Supports auto-update functionality
- ✅ Easy to deploy on servers

### Option 2: Install via pip (For Development)

If you prefer to use Python directly or need to modify the code:

```bash
# Install from PyPI
pip install gh-release-downloader

# Or install from source
git clone https://github.com/gisce/gh-release-downloader.git
cd gh-release-downloader
pip install -e .
```

**Note:** Auto-update functionality only works with binary installations. When using pip, update manually with:
```bash
pip install --upgrade gh-release-downloader
```

### Environment Setup

Set up your GitHub token as an environment variable:

```bash
# Add to your ~/.bashrc, ~/.zshrc, or /etc/environment
export GITHUB_TOKEN="your_personal_access_token_here"
```

To create a GitHub personal access token:
1. Go to GitHub Settings → Developer settings → Personal access tokens → Tokens (classic)
2. Click "Generate new token (classic)"
3. Give it a descriptive name (e.g., "gh-release-downloader")
4. Select scopes:
   - For private repositories: Check `repo` (full control)
   - For public repositories only: Check `public_repo`
5. Click "Generate token" and copy it immediately
6. Set the token as shown above

**Note:** GitHub also offers fine-grained tokens with more granular permissions. If using fine-grained tokens, ensure the token has read access to repository contents and metadata.

## Usage

### Basic Usage

The basic command structure is:

```bash
gh-release-downloader <owner/repo> [OPTIONS]
```

**Simple example** - Download the latest release:

```bash
gh-release-downloader gisce/powerp-frontend --output-dir /var/www/app
```

### Command-Line Options

#### Required Arguments

- `REPO`: The GitHub repository in format `owner/repo` (e.g., `gisce/powerp-frontend`)

#### Common Options

- `--output-dir PATH`: Directory where assets will be downloaded (default: current directory)
- `--version`: Show the version and exit
- `--help`: Show help message and exit

#### Version Filtering Options

- `--version-prefix PREFIX`: Filter releases by version prefix (e.g., `v1`, `v2.3`)
- `--pre-release`: Include pre-release versions (beta, rc, etc.)
- `--pre-release-type TYPE`: Filter for specific pre-release type string in the tag

#### Slack Notification Options

- `--webhook-url URL`: Slack webhook URL for notifications
- `--url-client URL`: Client URL to include in the Slack notification message
- `--include-release-body`: Include the full release notes in Slack notifications

#### Auto-Update Options

- `--auto-update / --no-auto-update`: Enable/disable automatic updates (enabled by default for binary installations)

### Understanding --pre-release and --pre-release-type

These options allow you to target specific types of releases:

#### --pre-release

By default, `gh-release-downloader` only downloads stable releases. Use `--pre-release` to include pre-release versions:

```bash
# Download the latest pre-release
gh-release-downloader myorg/myapp --pre-release --output-dir /var/www/staging
```

**When to use:**
- Testing new features before stable release
- Deploying to staging environments
- Following development versions

#### --pre-release-type

This option filters releases by a specific string in the tag name. It automatically implies `--pre-release`.

**Common pre-release types:**
- `alpha` - Early development versions (e.g., `v1.0.0-alpha1`)
- `beta` - Feature-complete but not fully tested (e.g., `v1.0.0-beta2`)
- `rc` - Release candidates, final testing before stable (e.g., `v1.0.0-rc1`)

```bash
# Download only release candidates
gh-release-downloader myorg/myapp --pre-release-type rc --output-dir /var/www/rc

# Download only beta releases
gh-release-downloader myorg/myapp --pre-release-type beta --output-dir /var/www/beta

# Download only alpha releases
gh-release-downloader myorg/myapp --pre-release-type alpha --output-dir /var/www/alpha
```

**Example workflow:**
```bash
# Production server - only stable releases
gh-release-downloader myorg/myapp --output-dir /var/www/production

# Staging server - release candidates
gh-release-downloader myorg/myapp --pre-release-type rc --output-dir /var/www/staging

# Development server - all pre-releases
gh-release-downloader myorg/myapp --pre-release --output-dir /var/www/dev
```

### Complete Usage Examples

**Example 1: Basic download with Slack notification**
```bash
gh-release-downloader gisce/powerp-frontend \
  --output-dir /var/www/app \
  --webhook-url "https://hooks.slack.com/services/YOUR/WEBHOOK/URL" \
  --url-client "https://app.example.com"
```

**Example 2: Download with release notes in Slack**
```bash
gh-release-downloader gisce/powerp-frontend \
  --output-dir /var/www/app \
  --webhook-url "https://hooks.slack.com/services/YOUR/WEBHOOK/URL" \
  --url-client "https://app.example.com" \
  --include-release-body
```

**Example 3: Download specific version prefix**
```bash
# Only download releases starting with "v2"
gh-release-downloader myorg/myapp \
  --version-prefix "v2" \
  --output-dir /var/www/app
```

**Example 4: Download release candidates without auto-update**
```bash
gh-release-downloader myorg/myapp \
  --pre-release-type rc \
  --output-dir /var/www/staging \
  --no-auto-update
```

## Auto-Update Functionality

**Auto-update is enabled by default** for binary installations. The tool automatically checks for and installs updates before executing your download request.

### How Auto-Update Works

When you run `gh-release-downloader`:

1. **Checks for updates**: Queries the GitHub repository for newer versions
2. **Downloads new version**: If available, downloads the latest binary
3. **Replaces itself**: Safely replaces the current binary with the new one
4. **Re-executes**: Automatically runs again with your original arguments

### When Auto-Update is Available

| Installation Method | Auto-Update Support |
|---------------------|---------------------|
| Pre-built binary | ✅ Yes (automatic) |
| PyPI/pip installation | ❌ No (manual update required) |
| Running from source | ❌ No (manual update required) |

### Controlling Auto-Update

**Disable auto-update** (useful for CI/CD or testing specific versions):
```bash
gh-release-downloader myorg/myapp --no-auto-update
```

**Manual update for pip installations**:
```bash
pip install --upgrade gh-release-downloader
```

### Version Checking

Check your current version:
```bash
gh-release-downloader --version
```

### Pre-release Auto-Updates

If you're using a pre-release version (e.g., `0.8.0-rc1`), the auto-update will also check for newer pre-releases. This ensures you stay on the cutting edge if you're testing beta features.

## Automating with Cron

One of the most common use cases is to run `gh-release-downloader` periodically to automatically deploy new releases. Here's how to set it up with cron:

### Basic Crontab Setup

Edit your crontab:
```bash
crontab -e
```

Add an entry to check for updates every hour:
```cron
# Check for new releases every hour at minute 0
0 * * * * /usr/local/bin/gh-release-downloader myorg/myapp --output-dir /var/www/app >> /var/log/gh-release-downloader.log 2>&1
```

### Crontab Examples

**Check every 30 minutes:**
```cron
# At minute 0 and 30 of every hour
*/30 * * * * /usr/local/bin/gh-release-downloader gisce/powerp-frontend --output-dir /var/www/app
```

**Check once daily at 3 AM:**
```cron
# At 03:00 every day
0 3 * * * /usr/local/bin/gh-release-downloader gisce/powerp-frontend --output-dir /var/www/app
```

**Check every 15 minutes with Slack notifications:**
```cron
# Every 15 minutes (token set in environment variables section at top of crontab)
*/15 * * * * /usr/local/bin/gh-release-downloader myorg/myapp \
  --output-dir /var/www/app \
  --webhook-url "https://hooks.slack.com/services/YOUR/WEBHOOK/URL" \
  --url-client "https://app.example.com" \
  >> /var/log/gh-release-downloader.log 2>&1
```

**Multiple environments with different schedules:**
```cron
# Production: Check every 2 hours for stable releases
0 */2 * * * /usr/local/bin/gh-release-downloader myorg/myapp --output-dir /var/www/production

# Staging: Check every 30 minutes for release candidates
*/30 * * * * /usr/local/bin/gh-release-downloader myorg/myapp --pre-release-type rc --output-dir /var/www/staging

# Development: Check every 10 minutes for all pre-releases
*/10 * * * * /usr/local/bin/gh-release-downloader myorg/myapp --pre-release --output-dir /var/www/dev
```

### Full Production Example

Here's a complete crontab configuration for a production server:

```cron
# Environment variables (set at the top of crontab)
# For better security, keep tokens in a separate file with restricted permissions
SHELL=/bin/bash
PATH=/usr/local/sbin:/usr/local/bin:/sbin:/bin:/usr/sbin:/usr/bin

# Production frontend - every hour
# Note: GITHUB_TOKEN should be set as a system environment variable or sourced from a secure file
0 * * * * export GITHUB_TOKEN=$(cat ~/.github_token) && /usr/local/bin/gh-release-downloader gisce/powerp-frontend \
  --output-dir /var/www/production \
  --webhook-url "https://hooks.slack.com/services/XXX/YYY/ZZZ" \
  --url-client "https://app.example.com" \
  --include-release-body \
  >> /var/log/frontend-updater.log 2>&1

# Staging frontend - every 20 minutes, include RC releases
*/20 * * * * export GITHUB_TOKEN=$(cat ~/.github_token) && /usr/local/bin/gh-release-downloader gisce/powerp-frontend \
  --pre-release-type rc \
  --output-dir /var/www/staging \
  --webhook-url "https://hooks.slack.com/services/XXX/YYY/ZZZ" \
  --url-client "https://staging.example.com" \
  >> /var/log/frontend-staging-updater.log 2>&1
```

**Security note:** Create a secure token file:
```bash
# Create a file with restricted permissions
echo "YOUR_GITHUB_TOKEN_HERE" > ~/.github_token
chmod 600 ~/.github_token
```

### Important Cron Considerations

1. **Use absolute paths**: Always use full paths to executables (`/usr/local/bin/gh-release-downloader`, not just `gh-release-downloader`)

2. **Secure token storage** (IMPORTANT for security):
   - **Never** store tokens directly in crontab commands or environment variables section
   - Store tokens in a separate file with restricted permissions: `chmod 600 ~/.github_token`
   - Source the token file in your cron command: `export GITHUB_TOKEN=$(cat ~/.github_token)`
   - Alternative: Set `GITHUB_TOKEN` as a system-wide environment variable in `/etc/environment` (requires proper system permissions)

3. **Set environment variables**: Cron has a limited environment. Either:
   - Set non-sensitive variables at the top of crontab (PATH, SHELL, etc.)
   - Source your profile: `*/30 * * * * . ~/.bashrc && gh-release-downloader ...`
   - Load tokens from secure files as shown above

4. **Log output**: Redirect output to a log file for debugging:
   ```cron
   */30 * * * * command >> /var/log/updater.log 2>&1
   ```

5. **Test your cron command**: Before adding to cron, test the exact command manually to ensure it works

6. **Monitor logs**: Regularly check your log files to ensure the cron job is running successfully

7. **File permissions**: Ensure your crontab and token files have appropriate permissions
   ```bash
   chmod 600 ~/.github_token  # Token file readable only by you
   crontab -l > /tmp/mycron   # Backup your crontab
   ```

### Cron Time Format Quick Reference

```
* * * * * command
│ │ │ │ │
│ │ │ │ └─── Day of week (0-6, Sunday=0; some systems also accept 7 for Sunday)
│ │ │ └───── Month (1-12)
│ │ └─────── Day of month (1-31)
│ └───────── Hour (0-23)
└─────────── Minute (0-59)
```

**Examples:**
- `*/5 * * * *` - Every 5 minutes
- `0 */2 * * *` - Every 2 hours
- `0 9 * * 1-5` - At 9 AM, Monday through Friday
- `30 2 1 * *` - At 2:30 AM on the first day of every month

## Slack Notifications

`gh-release-downloader` can send notifications to Slack when new releases are deployed, keeping your team informed in real-time.

### Setting Up Slack Notifications

1. **Create a Slack Webhook:**
   - Go to your Slack workspace settings
   - Navigate to "Incoming Webhooks" under Custom Integrations
   - Create a new webhook for the desired channel
   - Copy the webhook URL (looks like: `https://hooks.slack.com/services/T00000000/B00000000/XXXXXXXXXXXX`)

2. **Use the webhook in your command:**
   ```bash
   gh-release-downloader myorg/myapp \
     --webhook-url "https://hooks.slack.com/services/YOUR/WEBHOOK/URL" \
     --url-client "https://app.example.com"
   ```

### Basic Slack Notification

By default, Slack notifications include:
- 🚀 Release tag and link to GitHub release
- 🔗 Deployment URL (specified via `--url-client`)

**Example notification:**
```
🚀 New release v2.0.0 deployed at https://app.example.com
```

### Including Release Body in Slack Notifications

To include the full release notes in your Slack notification, use the `--include-release-body` flag:

```bash
gh-release-downloader myorg/myapp \
  --webhook-url "YOUR_SLACK_WEBHOOK_URL" \
  --url-client "https://app.example.com" \
  --include-release-body
```

When enabled, the notification will look like:

```
🚀 New release v2.0.0 deployed at https://app.example.com

Release notes:
• Added new authentication system
• Fixed critical security vulnerability
• Improved performance by 50%
```

The release notes are automatically converted from GitHub markdown to Slack-compatible format.

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

## Available Releases

`gh-release-downloader` is distributed in two formats to accommodate different use cases:

### 1. Static Binary (Recommended for Production)

**Download from GitHub Releases:** [Latest Release](https://github.com/gisce/gh-release-downloader/releases/latest)

The static binary is:
- **Self-contained**: No Python installation or dependencies required
- **Auto-updating**: Can update itself to newer versions automatically
- **Production-ready**: Perfect for deploying on servers
- **Cross-platform**: Built for Linux (more platforms coming soon)

**How it's built:**
- Compiled using PyInstaller
- Single executable file
- Includes all dependencies
- Created automatically via GitHub Actions on every tagged release

**Version naming:**
- Stable releases: `v1.0.0`, `v1.1.0`, etc.
- Release candidates: `v1.0.0-rc`, `v1.1.0-rc1`, etc.

### 2. Python Package (PyPI)

**Install via pip:** `pip install gh-release-downloader`

The PyPI package is:
- **For developers**: Ideal for development and testing
- **Modifiable**: Source code accessible for customization
- **Requires Python 3.6+**: Must have Python and dependencies installed
- **Manual updates**: Update with `pip install --upgrade`

**When to use:**
- Development and testing
- Custom modifications needed
- Python environment already available
- Integration into other Python projects

### Choosing the Right Installation

| Use Case | Recommended Installation |
|----------|--------------------------|
| Production server deployment | 📦 Static Binary |
| CI/CD pipelines | 📦 Static Binary |
| Development and testing | 🐍 PyPI Package |
| Custom modifications | 🐍 PyPI Package |
| No Python available | 📦 Static Binary |
| Python project integration | 🐍 PyPI Package |

### Release Schedule

- **Stable releases** are created when new features are tested and ready
- **Release candidates (RC)** are published for testing before stable releases
- **Auto-update** ensures you always have the latest version (for binary installations)

### Finding Releases

Browse all releases on GitHub: [https://github.com/gisce/gh-release-downloader/releases](https://github.com/gisce/gh-release-downloader/releases)

Each release includes:
- 📦 Pre-built binary (`gh-release-downloader`)
- 📝 Release notes with changes and improvements
- 🏷️ Version tag for reference

## Troubleshooting

### Common Issues

**"GitHub token not found in environment variables"**
- Ensure `GITHUB_TOKEN` is set: `export GITHUB_TOKEN="your_token"`
- Check token has correct permissions (repo or public_repo scope)

**"Failed to fetch releases"**
- Verify the repository name format is correct: `owner/repo`
- Check your GitHub token is valid and not expired
- Ensure you have access to the repository (especially for private repos)

**"No matching releases found"**
- Check that releases exist in the target repository
- Verify your filters (`--version-prefix`, `--pre-release-type`) are correct
- Try without filters to see all releases

**"Auto-update is only supported for binary installations"**
- This is expected when running from pip or source
- Update manually: `pip install --upgrade gh-release-downloader`

**Cron job not running**
- Test the command manually first
- Check cron logs: `grep CRON /var/log/syslog`
- Verify environment variables are set in crontab
- Use absolute paths for all commands and files

## Contributions

Contributions to this project are welcome! Please:
- Open an issue for bug reports or feature requests
- Submit a Pull Request with your improvements
- Follow the existing code style and conventions

## License

[MIT](LICENSE)
