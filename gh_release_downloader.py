import os
import requests
import click
import json
import zipfile
import shutil
import semver

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

def markdown_to_slack_format(text):
    """
    Converts GitHub markdown to Slack-compatible format.
    
    Transformations:
    - Headers (# -> uppercase text, no #)
    - Links [text](url) -> <url|text>
    - Bold **text** and __text__ -> *text* (Slack format)
    - Italic *text* and _text_ -> _text_ (Slack format)
    - Lists (- or * -> •)
    - Code blocks and quotes are maintained
    - Removes unsupported markdown
    """
    import re
    
    if not text:
        return text
    
    lines = text.split('\n')
    converted_lines = []
    in_code_block = False
    
    for line in lines:
        # Check for code block delimiters
        if line.strip().startswith('```'):
            in_code_block = not in_code_block
            converted_lines.append(line)
            continue
        
        # Don't process lines inside code blocks
        if in_code_block:
            converted_lines.append(line)
            continue
        
        # Convert headers (# Header -> HEADER or with emoji)
        header_match = re.match(r'^(#{1,6})\s+(.+)$', line)
        if header_match:
            header_level = len(header_match.group(1))
            header_text = header_match.group(2).strip()
            # Convert to uppercase for emphasis
            if header_level == 1:
                line = f"*{header_text.upper()}*"
            elif header_level == 2:
                line = f"*{header_text}*"
            else:
                line = f"_{header_text}_"
        
        # Convert markdown links [text](url) to Slack format <url|text>
        line = re.sub(r'\[([^\]]+)\]\(([^\)]+)\)', r'<\2|\1>', line)
        
        # Convert bold: **text** or __text__ -> *text* (Slack format)
        line = re.sub(r'\*\*(.+?)\*\*', r'*\1*', line)
        line = re.sub(r'__(.+?)__', r'*\1*', line)
        
        # Convert italic: *text* -> _text_ (Slack format) - but be careful with bold
        # We need to handle this carefully to not interfere with bold
        # First, temporarily replace bold markers
        bold_placeholders = []
        def save_bold(match):
            bold_placeholders.append(match.group(0))
            return f"___BOLD_{len(bold_placeholders)-1}___"
        line = re.sub(r'\*[^*]+\*', save_bold, line)
        
        # Now convert remaining single asterisks (italic) to underscores
        line = re.sub(r'(?<!\*)\*(?!\*)([^*]+?)(?<!\*)\*(?!\*)', r'_\1_', line)
        
        # Restore bold markers
        for i, bold_text in enumerate(bold_placeholders):
            line = line.replace(f"___BOLD_{i}___", bold_text)
        
        # Also handle underscore italic: _text_ is already Slack format, but avoid double underscores
        # Single underscores are already italic in Slack, so we're good
        
        # Convert list markers (-, *, +) to bullet points
        line = re.sub(r'^(\s*)([-*+])\s+', r'\1• ', line)
        
        converted_lines.append(line)
    
    return '\n'.join(converted_lines)

def send_slack_notification(webhook_url, release, url_client):
    """
    Sends a notification to a Slack webhook.
    """
    message_text = f":rocket: New release <{release['html_url']}|{release['tag_name']}> deployed at {url_client}"
    if release.get('body'):
        # Convert markdown to Slack format
        formatted_body = markdown_to_slack_format(release['body'])
        message_text += f"\n\n*Release notes:*\n{formatted_body}"
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

@click.command()
@click.version_option(version=__version__)
@click.argument('repo')
@click.option('--pre-release', is_flag=True, help="Include pre-releases")
@click.option('--pre-release-type', default='', help="Check for this string in relase tag. This implies pre-release versions")
@click.option('--version-prefix', default='', help="Version prefix to filter releases")
@click.option('--webhook-url', help="Slack webhook URL for notifications")
@click.option('--url-client', help="Client URL to include in the Slack message")
@click.option('--output-dir', default='.', help="Directory to save the downloaded assets and the last release file")
def main(repo, pre_release, pre_release_type, version_prefix, webhook_url, url_client, output_dir):
    """
    Download assets from a GitHub release and notify via Slack if a webhook is provided.
    """
    token = os.getenv('GITHUB_TOKEN')
    if not token:
        raise click.ClickException("GitHub token not found in environment variables")

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
