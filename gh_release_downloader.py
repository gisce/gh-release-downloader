import os
import requests
import click
import json
import zipfile
import shutil
import semver
import sys
import platform
import stat

# Constants
SELF_REPO = 'gisce/gh-release-downloader'

try:
    from importlib.metadata import version
    __version__ = version("gh-release-downloader")
except Exception:
    # Fallback for development or if package is not installed
    __version__ = "0.0.0.dev"


def get_github_releases(repo, token, include_prerelease, pre_release_type, version_prefix):
    """
    Fetches the releases from a GitHub repository that start with a specific version prefix.
    """
    headers = {'Authorization': f'token {token}'}
    url = f"https://api.github.com/repos/{repo}/releases"
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        raise click.ClickException(f"Failed to fetch releases: {response.text}")

    releases = response.json()
    filtered_releases = [
        release for release in releases
            if release['tag_name'].startswith(version_prefix)
            and release['prerelease'] == include_prerelease
            and pre_release_type in release['tag_name']
    ]

    # Sort releases by semantic versioning
    def semver_sort_key(release):
        try:
            # Strip leading 'v'
            version_str = release['tag_name'].lstrip('v')
            return semver.VersionInfo.parse(version_str)
        except ValueError:
            return semver.VersionInfo(0, 0, 0)

    sorted_releases = sorted(filtered_releases, key=semver_sort_key, reverse=True)

    return sorted_releases

def download_assets(releases, token, output_dir):
    """
    Downloads assets from the provided releases and unzips if they are zip files.
    """
    headers = {
        'Authorization': f'token {token}',
        'Accept': 'application/octet-stream'
    }
    for release in releases:
        if not release['assets']:
            raise click.ClickException(f"No assets found for release {release['tag_name']}")

        for asset in release['assets']:
            asset_url = asset['url']  # Utilitzem 'url', no 'browser_download_url'
            response = requests.get(asset_url, headers=headers, stream=True)
            if response.status_code != 200:
                raise click.ClickException(f"Failed to download asset: {response.text}")

            filename = asset['name']
            filepath = os.path.join(output_dir, filename)
            os.makedirs(os.path.dirname(filepath), exist_ok=True)

            with open(filepath, 'wb') as file:
                for chunk in response.iter_content(chunk_size=128):
                    file.write(chunk)

            if filename.endswith('.zip'):
                unzip_file(filepath, output_dir)

            click.echo(f"Downloaded and extracted {filename}")

def unzip_file(zip_path, extract_to):
    """
    Unzips a zip file to the specified directory and then deletes the zip file.
    """
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_to)
    os.remove(zip_path)  # Elimina el fitxer .zip després de descomprimir-lo

    # Move .map files after extraction
    maps_dir = os.path.join(extract_to, 'static/maps')
    move_map_files(extract_to, maps_dir)

def save_last_downloaded_release(release, output_dir, filename='last_release.json'):
    """
    Saves the last downloaded release information to a file.
    """
    filepath = os.path.join(output_dir, filename)
    with open(filepath, 'w') as file:
        json.dump(release, file)

def load_last_downloaded_release(output_dir, filename='last_release.json'):
    """
    Loads the last downloaded release information from a file.
    """
    filepath = os.path.join(output_dir, filename)
    if os.path.exists(filepath):
        with open(filepath, 'r') as file:
            return json.load(file)
    return None

def send_slack_notification(webhook_url, release, url_client):
    """
    Sends a notification to a Slack webhook.
    """
    message_text = f":rocket: New release <{release['html_url']}|{release['tag_name']}> deployed at {url_client}"
    if release.get('body'):
        message_text += f"\n\n*Release notes:*\n{release['body']}"
    message = {"text": message_text}
    response = requests.post(webhook_url, json=message)
    if response.status_code != 200:
        raise click.ClickException(f"Failed to send Slack notification: {response.text}")

def move_map_files(source_dir, target_dir):
    """
    Moves all .map files from source_dir and its subdirectories to target_dir.
    """
    os.makedirs(target_dir, exist_ok=True)  # Create the target directory if it doesn't exist
    for root, dirs, files in os.walk(source_dir):
        for file in files:
            if file.endswith('.map'):
                source_file = os.path.join(root, file)
                target_file = os.path.join(target_dir, file)
                shutil.move(source_file, target_file)

def get_system_info():
    """
    Detects the current OS and architecture.
    Returns a tuple (os_name, architecture) normalized for binary selection.
    """
    system = platform.system().lower()
    machine = platform.machine().lower()
    
    # Normalize OS name
    if system == 'darwin':
        os_name = 'macos'
    else:
        os_name = system
    
    # Normalize architecture
    if machine in ['x86_64', 'amd64']:
        arch = 'x86_64'
    elif machine in ['aarch64', 'arm64']:
        arch = 'arm64'
    else:
        arch = machine
    
    return os_name, arch

def normalize_version_to_semver(version_string):
    """
    Normalizes a PEP 440 version string to semver format.
    Converts formats like '0.5.0rc1' to '0.5.0-rc1'.
    """
    import re
    # Pattern to match PEP 440 pre-release versions (e.g., 0.5.0rc1, 1.0.0a1, 2.0.0b2)
    # and convert them to semver format (e.g., 0.5.0-rc1, 1.0.0-a1, 2.0.0-b2)
    pattern = r'^(\d+\.\d+\.\d+)((?:a|alpha|b|beta|rc)[\d]+)(.*)$'
    match = re.match(pattern, version_string)
    if match:
        version_core = match.group(1)
        prerelease = match.group(2)
        rest = match.group(3)
        # Add a dash before the pre-release identifier
        return f"{version_core}-{prerelease}{rest}"
    return version_string

def check_for_updates(token):
    """
    Checks if there is a newer version available for gh-release-downloader.
    Returns the latest release if a newer version exists, None otherwise.
    If current version is a pre-release, also checks for pre-release versions.
    """
    current_version = __version__
    # Normalize PEP 440 version to semver format
    normalized_version = normalize_version_to_semver(current_version)
    
    try:
        current_semver = semver.VersionInfo.parse(normalized_version)
    except ValueError:
        click.echo(f"Warning: Could not parse current version '{current_version}' (normalized: '{normalized_version}')")
        return None
    
    # If current version is a pre-release, also check for pre-release versions
    include_prerelease = bool(current_semver.prerelease)
    
    # Get releases from the gh-release-downloader repository
    releases = get_github_releases(SELF_REPO, token, include_prerelease, '', 'v')
    
    if not releases:
        click.echo("No releases found for gh-release-downloader")
        return None
    
    latest_release = releases[0]
    latest_version_str = latest_release['tag_name'].lstrip('v')
    
    try:
        latest_semver = semver.VersionInfo.parse(latest_version_str)
    except ValueError:
        click.echo(f"Warning: Could not parse latest version '{latest_version_str}'")
        return None
    
    if latest_semver > current_semver:
        return latest_release
    
    return None

def download_and_replace_binary(release, token):
    """
    Downloads the appropriate binary for the current system and replaces the current executable.
    Note: This assumes the GitHub release contains a single binary named 'gh-release-downloader'.
    For multi-platform releases, extend the logic to select the correct binary based on OS/arch.
    """
    os_name, arch = get_system_info()
    
    # Find the appropriate asset (assuming the binary is named 'gh-release-downloader')
    binary_asset = None
    for asset in release['assets']:
        # Note: Current implementation assumes a single binary.
        # For multi-platform support, extend this to match OS/arch in filename
        if asset['name'] == 'gh-release-downloader':
            binary_asset = asset
            break
    
    if not binary_asset:
        raise click.ClickException(f"No suitable binary found for {os_name}/{arch} in release {release['tag_name']}")
    
    # Download the binary
    headers = {
        'Authorization': f'token {token}',
        'Accept': 'application/octet-stream'
    }
    
    click.echo(f"Downloading {binary_asset['name']}...")
    response = requests.get(binary_asset['url'], headers=headers, stream=True)
    if response.status_code != 200:
        raise click.ClickException(f"Failed to download binary: {response.text}")
    
    # Determine if we're running as a script or as a PyInstaller binary
    if getattr(sys, 'frozen', False):
        # Running as PyInstaller binary
        target_path = sys.executable
    else:
        # Running as a script - cannot self-update
        raise click.ClickException("Auto-update is only supported for binary installations. Please update manually with: pip install --upgrade gh-release-downloader")
    
    # Create a temporary file for the new binary
    temp_path = target_path + '.new'
    
    try:
        # Write the new binary
        with open(temp_path, 'wb') as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)
        
        # Make it executable
        st = os.stat(temp_path)
        os.chmod(temp_path, st.st_mode | stat.S_IEXEC | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
        
        # Backup the old binary
        backup_path = target_path + '.old'
        if os.path.exists(backup_path):
            os.remove(backup_path)
        
        # Replace the binary
        os.rename(target_path, backup_path)
        os.rename(temp_path, target_path)
        
        click.echo(f"Successfully updated to version {release['tag_name']}")
        
        # Clean up backup
        if os.path.exists(backup_path):
            os.remove(backup_path)
        
        return True
        
    except Exception as e:
        # Rollback on error
        if os.path.exists(temp_path):
            os.remove(temp_path)
        
        backup_path = target_path + '.old'
        if os.path.exists(backup_path) and not os.path.exists(target_path):
            os.rename(backup_path, target_path)
        
        raise click.ClickException(f"Failed to update binary: {str(e)}")

def perform_auto_update(token):
    """
    Performs the auto-update check and update if a newer version is available.
    """
    click.echo("Checking for updates...")
    
    latest_release = check_for_updates(token)
    
    if not latest_release:
        click.echo("You are already running the latest version.")
        return False
    
    current_version = __version__
    latest_version = latest_release['tag_name']
    
    click.echo(f"New version available: {latest_version} (current: v{current_version})")
    
    # Download and replace the binary
    download_and_replace_binary(latest_release, token)
    
    # Re-execute with the same arguments (excluding --auto-update and --no-auto-update)
    args = [arg for arg in sys.argv if arg not in ['--auto-update', '--no-auto-update']]
    click.echo(f"Re-executing with updated binary...")
    os.execv(sys.executable, args)

@click.command()
@click.version_option(version=__version__)
@click.argument('repo')
@click.option('--pre-release', is_flag=True, help="Include pre-releases")
@click.option('--pre-release-type', default='', help="Check for this string in release tag. This implies pre-release versions")
@click.option('--version-prefix', default='', help="Version prefix to filter releases")
@click.option('--webhook-url', help="Slack webhook URL for notifications")
@click.option('--url-client', help="Client URL to include in the Slack message")
@click.option('--output-dir', default='.', help="Directory to save the downloaded assets and the last release file")
@click.option('--auto-update/--no-auto-update', default=True, help="Check for updates to gh-release-downloader and auto-update if available (enabled by default)")
def main(repo, pre_release, pre_release_type, version_prefix, webhook_url, url_client, output_dir, auto_update):
    """
    Download assets from a GitHub release and notify via Slack if a webhook is provided.
    """
    token = os.getenv('GITHUB_TOKEN')
    if not token:
        raise click.ClickException("GitHub token not found in environment variables")

    # Perform auto-update check if requested
    if auto_update:
        perform_auto_update(token)
        # If we reach here, no update was needed, continue with normal execution

    last_downloaded = load_last_downloaded_release(output_dir)
    if pre_release_type:
        pre_release = True
    releases = get_github_releases(repo, token, pre_release, pre_release_type, version_prefix)

    if not releases:
        click.echo("No matching releases found.")
        return

    latest_release = releases[0]  # Assuming the first one is the latest
    if not latest_release['assets']:
        raise click.ClickException(f"No assets found for the latest release {latest_release['tag_name']}")

    if last_downloaded and last_downloaded['tag_name'] == latest_release['tag_name']:
        click.echo(f"Latest release {last_downloaded['tag_name']} is already downloaded.")
        return

    download_assets([latest_release], token, output_dir)
    save_last_downloaded_release(latest_release, output_dir)

    if webhook_url and url_client:
        send_slack_notification(webhook_url, latest_release, url_client)
        click.echo("Slack notification sent.")


if __name__ == "__main__":
    main()
