#!/usr/bin/env python3
"""
Example demonstrating how to use the markdown_to_slack_format function
from other scripts or bots that need to send Slack notifications.
"""

from gh_release_downloader import markdown_to_slack_format


def example_slack_bot():
    """
    Example of using markdown_to_slack_format in a Slack bot
    """
    # Example: GitHub release notes in markdown format
    github_markdown = """# Version 2.0.0 Released! 🎉

## What's New

- Added **authentication** with [OAuth2](https://oauth.net/)
- Implemented __user profiles__ and settings
- Added support for *multiple languages*

## Bug Fixes

- Fixed critical _security vulnerability_
- Resolved [issue #123](https://github.com/example/repo/issues/123)
- Improved performance by 50%

## Installation

```bash
pip install gh-release-downloader==2.0.0
```

## Breaking Changes

> **Warning**: This version includes breaking changes. Please review the migration guide.

## Contributors

- [@user1](https://github.com/user1)
- [@user2](https://github.com/user2)

Thank you to all contributors!
"""

    # Convert to Slack format
    slack_formatted = markdown_to_slack_format(github_markdown)
    
    print("=" * 60)
    print("ORIGINAL GITHUB MARKDOWN:")
    print("=" * 60)
    print(github_markdown)
    print("\n" + "=" * 60)
    print("CONVERTED TO SLACK FORMAT:")
    print("=" * 60)
    print(slack_formatted)
    
    # In a real bot, you would send this to Slack:
    # requests.post(webhook_url, json={"text": slack_formatted})
    
    return slack_formatted


def example_custom_notification():
    """
    Example of custom notification formatting
    """
    message = """## Deployment Notification

The application has been deployed to production!

- **Version**: v1.2.3
- **Environment**: Production
- **Status**: Success
- **Link**: [View Deployment](https://example.com/deployments/123)

### Changes Included

- Bug fixes for [critical issue](https://issues.example.com/456)
- Performance improvements
- New __admin dashboard__ feature

```
Deployment ID: deploy-abc123
Time: 2024-01-15 10:30:00 UTC
```

> **Note**: All services are operational
"""
    
    slack_message = markdown_to_slack_format(message)
    print("\n\n" + "=" * 60)
    print("CUSTOM NOTIFICATION EXAMPLE:")
    print("=" * 60)
    print(slack_message)
    
    return slack_message


if __name__ == "__main__":
    print("Markdown to Slack Format Transformer - Examples")
    print("=" * 60)
    
    # Run examples
    example_slack_bot()
    example_custom_notification()
    
    print("\n" + "=" * 60)
    print("Examples completed successfully!")
    print("=" * 60)
