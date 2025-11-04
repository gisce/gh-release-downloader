"""
Tests for the Slack notification functionality
"""
import unittest
from unittest.mock import Mock, patch
from gh_release_downloader import send_slack_notification


class TestSlackNotification(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures"""
        self.webhook_url = "https://hooks.slack.com/services/TEST/WEBHOOK"
        self.url_client = "https://example.com"
        self.release = {
            'html_url': 'https://github.com/test/repo/releases/tag/v1.0.0',
            'tag_name': 'v1.0.0',
            'body': '## What\'s New\n\n- Added **new feature**\n- Fixed bug'
        }
    
    @patch('gh_release_downloader.requests.post')
    def test_notification_without_body_by_default(self, mock_post):
        """Test that release body is NOT included by default"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response
        
        send_slack_notification(self.webhook_url, self.release, self.url_client)
        
        # Verify the function was called
        mock_post.assert_called_once()
        
        # Get the message that was sent
        call_args = mock_post.call_args
        message = call_args[1]['json']
        
        # Verify that the body is NOT in the message
        self.assertNotIn('Release notes:', message['text'])
        self.assertNotIn('new feature', message['text'])
        self.assertNotIn('Fixed bug', message['text'])
        
        # Verify that basic info is included
        self.assertIn('v1.0.0', message['text'])
        self.assertIn('https://example.com', message['text'])
    
    @patch('gh_release_downloader.requests.post')
    def test_notification_with_body_when_enabled(self, mock_post):
        """Test that release body IS included when explicitly enabled"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response
        
        send_slack_notification(self.webhook_url, self.release, self.url_client, include_body=True)
        
        # Verify the function was called
        mock_post.assert_called_once()
        
        # Get the message that was sent
        call_args = mock_post.call_args
        message = call_args[1]['json']
        
        # Verify that the body IS in the message
        self.assertIn('Release notes:', message['text'])
        self.assertIn('new feature', message['text'])
        self.assertIn('Fixed bug', message['text'])
        
        # Verify that basic info is also included
        self.assertIn('v1.0.0', message['text'])
        self.assertIn('https://example.com', message['text'])
    
    @patch('gh_release_downloader.requests.post')
    def test_notification_without_body_when_explicitly_disabled(self, mock_post):
        """Test that release body is NOT included when explicitly disabled"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response
        
        send_slack_notification(self.webhook_url, self.release, self.url_client, include_body=False)
        
        # Verify the function was called
        mock_post.assert_called_once()
        
        # Get the message that was sent
        call_args = mock_post.call_args
        message = call_args[1]['json']
        
        # Verify that the body is NOT in the message
        self.assertNotIn('Release notes:', message['text'])
        self.assertNotIn('new feature', message['text'])
    
    @patch('gh_release_downloader.requests.post')
    def test_notification_with_empty_body(self, mock_post):
        """Test notification when release has no body"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response
        
        release_no_body = {
            'html_url': 'https://github.com/test/repo/releases/tag/v1.0.0',
            'tag_name': 'v1.0.0',
            'body': None
        }
        
        # Should work fine even with include_body=True
        send_slack_notification(self.webhook_url, release_no_body, self.url_client, include_body=True)
        
        # Verify the function was called
        mock_post.assert_called_once()
        
        # Get the message that was sent
        call_args = mock_post.call_args
        message = call_args[1]['json']
        
        # Verify that Release notes section is not added when body is None
        self.assertNotIn('Release notes:', message['text'])
        
        # Verify that basic info is included
        self.assertIn('v1.0.0', message['text'])


if __name__ == '__main__':
    unittest.main()
