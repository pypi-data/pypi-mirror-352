# Facebook Collector

A Python library for collecting data from Facebook using Selenium and GraphQL.

## Features

- Collect posts by keyword search
- Collect posts by hashtag
- Collect post comments
- Collect profile information
- Handle authentication via cookies
- Automatic scrolling and pagination
- Error handling and retry mechanisms

## Installation

```bash
pip install -r requirements.txt
```

## Usage

### Initialize Collector

```python
from facebook_collector.keywords import FacebookKeywordCollector
from facebook_collector.hashtag import FacebookHashtagCollector
from facebook_collector.post_comment import FacebookPostCommentCollector

# Initialize with your Facebook cookie
cookie = "your_facebook_cookie_here"

# For keyword search
keyword_collector = FacebookKeywordCollector(cookie)
posts = keyword_collector.collect_posts_by_keyword("your_keyword")

# For hashtag search
hashtag_collector = FacebookHashtagCollector(cookie)
posts = hashtag_collector.collect_posts_by_hashtag("your_hashtag")

# For post comments
comment_collector = FacebookPostCommentCollector(cookie)
comments = comment_collector.collect_comments_by_post("post_id")
```

### Configuration

Each collector can be configured with:
- Maximum number of items to collect
- Maximum number of retries
- Custom timeouts and delays

## Project Structure

```
facebook_collector/
├── __init__.py
├── keyword.py              # Keyword search collector
├── hashtag.py              # Hashtag search collector
├── post_comment.py         # Post comment collector
├── profile_handler/
│   ├── __init__.py
│   └── facebook_graphql_collector.py  # GraphQL data collection
├── constant.py             # Constants and configurations
└── utils.py               # Utility functions
```

## Requirements

- Python 3.7+
- Selenium
- Chrome/Chromium browser
- ChromeDriver

## License

MIT License 