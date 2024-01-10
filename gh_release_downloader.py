import os
import requests
import click
import json
import zipfile
import shutil
import typing as t


class AlreadyLatestVersion(click.ClickException):
    exit_code = 17

    def show(self, file: t.Optional[t.IO[t.Any]] = None) -> None:
        if file is None:
            file = click.exceptions.get_text_stderr()

        click.echo("{message}".format(message=self.format_message()), file=file)


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
    return filtered_releases

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
    message = {
        "text": f":rocket: New release <{release['html_url']}|{release['tag_name']}> deployed at {url_client}"
    }
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
        raise AlreadyLatestVersion(f"Latest release {last_downloaded['tag_name']} is already downloaded.")

    download_assets([latest_release], token, output_dir)
    save_last_downloaded_release(latest_release, output_dir)

    if webhook_url and url_client:
        send_slack_notification(webhook_url, latest_release, url_client)
        click.echo("Slack notification sent.")


if __name__ == "__main__":
    main()
