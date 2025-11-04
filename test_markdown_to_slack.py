"""
Tests for the markdown_to_slack_format function
"""
import unittest
from gh_release_downloader import markdown_to_slack_format


class TestMarkdownToSlackFormat(unittest.TestCase):
    
    def test_headers_h1(self):
        """Test H1 headers are converted to uppercase bold"""
        input_text = "# Main Header"
        expected = "*MAIN HEADER*"
        result = markdown_to_slack_format(input_text)
        self.assertEqual(result, expected)
    
    def test_headers_h2(self):
        """Test H2 headers are converted to bold"""
        input_text = "## Section Header"
        expected = "*Section Header*"
        result = markdown_to_slack_format(input_text)
        self.assertEqual(result, expected)
    
    def test_headers_h3(self):
        """Test H3 headers are converted to italic"""
        input_text = "### Subsection"
        expected = "_Subsection_"
        result = markdown_to_slack_format(input_text)
        self.assertEqual(result, expected)
    
    def test_links(self):
        """Test markdown links are converted to Slack format"""
        input_text = "Check [this link](https://example.com) for more info"
        expected = "Check <https://example.com|this link> for more info"
        result = markdown_to_slack_format(input_text)
        self.assertEqual(result, expected)
    
    def test_multiple_links(self):
        """Test multiple links in same line"""
        input_text = "See [link1](https://example1.com) and [link2](https://example2.com)"
        expected = "See <https://example1.com|link1> and <https://example2.com|link2>"
        result = markdown_to_slack_format(input_text)
        self.assertEqual(result, expected)
    
    def test_bold_double_asterisk(self):
        """Test bold with ** is converted to Slack format"""
        input_text = "This is **bold text** in markdown"
        expected = "This is *bold text* in markdown"
        result = markdown_to_slack_format(input_text)
        self.assertEqual(result, expected)
    
    def test_bold_double_underscore(self):
        """Test bold with __ is converted to Slack format"""
        input_text = "This is __bold text__ in markdown"
        expected = "This is *bold text* in markdown"
        result = markdown_to_slack_format(input_text)
        self.assertEqual(result, expected)
    
    def test_lists(self):
        """Test list items are converted to bullet points"""
        input_text = "- Item 1\n- Item 2\n* Item 3"
        expected = "• Item 1\n• Item 2\n• Item 3"
        result = markdown_to_slack_format(input_text)
        self.assertEqual(result, expected)
    
    def test_indented_lists(self):
        """Test indented list items maintain indentation"""
        input_text = "- Item 1\n  - Subitem 1\n  - Subitem 2"
        expected = "• Item 1\n  • Subitem 1\n  • Subitem 2"
        result = markdown_to_slack_format(input_text)
        self.assertEqual(result, expected)
    
    def test_code_blocks(self):
        """Test code blocks are preserved"""
        input_text = "```python\ndef hello():\n    print('Hello')\n```"
        expected = "```python\ndef hello():\n    print('Hello')\n```"
        result = markdown_to_slack_format(input_text)
        self.assertEqual(result, expected)
    
    def test_code_blocks_no_processing(self):
        """Test that markdown inside code blocks is not processed"""
        input_text = "```\n# This is not a header\n**not bold**\n[link](url)\n```"
        expected = "```\n# This is not a header\n**not bold**\n[link](url)\n```"
        result = markdown_to_slack_format(input_text)
        self.assertEqual(result, expected)
    
    def test_quotes(self):
        """Test that quotes are preserved"""
        input_text = "> This is a quote\n> Second line"
        expected = "> This is a quote\n> Second line"
        result = markdown_to_slack_format(input_text)
        self.assertEqual(result, expected)
    
    def test_empty_text(self):
        """Test empty or None text"""
        self.assertIsNone(markdown_to_slack_format(None))
        self.assertEqual(markdown_to_slack_format(""), "")
    
    def test_complex_example(self):
        """Test a complex example with multiple markdown elements"""
        input_text = """# Release v1.0.0

## What's New

- Added **new feature** for [users](https://example.com)
- Fixed bug in __authentication__
- Improved performance

## Installation

```bash
pip install package
```

> **Note**: This is a breaking change"""
        
        expected = """*RELEASE V1.0.0*

*What's New*

• Added *new feature* for <https://example.com|users>
• Fixed bug in *authentication*
• Improved performance

*Installation*

```bash
pip install package
```

> *Note*: This is a breaking change"""
        
        result = markdown_to_slack_format(input_text)
        self.assertEqual(result, expected)
    
    def test_mixed_bold_and_links(self):
        """Test bold text with links"""
        input_text = "**Check [this](https://example.com)** for details"
        expected = "*Check <https://example.com|this>* for details"
        result = markdown_to_slack_format(input_text)
        self.assertEqual(result, expected)


if __name__ == '__main__':
    unittest.main()
