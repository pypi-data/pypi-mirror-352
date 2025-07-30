# Instagram Collector

A Python library for collecting Instagram data including hashtag posts, tagged posts, brand posts, and comments.

## Features

- Collect posts by hashtag
- Collect tagged posts for a user
- Collect posts from brand accounts
- Collect comments from posts
- Support for multiple API providers (RocketAPI and SocialAPI4)
- Rate limiting and error handling
- Pagination support
- Time-based filtering

## Installation

```bash
pip install instagram-collector
```

## Usage

### Initialize Collector

```python
from instagram_collector import InstagramCollector

# Initialize with your RapidAPI key
api_key = "YOUR_RAPID_API_KEY"
collector = InstagramCollector(api_key=api_key, api="rocketapi")  # or "social4"
```

## Configuration

The library supports various configuration options:

- `api`: Choose between "rocketapi" or "social4" (default: "rocketapi")
- `max_hashtag_post_retry`: Maximum retries for hashtag posts (default: 3)
- `max_tagged_post_retry`: Maximum retries for tagged posts (default: 3)
- `max_brand_post_retry`: Maximum retries for brand posts (default: 3)
- `max_comment_retry`: Maximum retries for comments (default: 3)
- `rate_limit_delay`: Delay between API calls in seconds (default: 2)

## Error Handling

The library includes built-in error handling and retry mechanisms:

- Automatic retry on API failures
- Rate limiting to prevent API throttling
- Time-based filtering to limit data collection
- Exception handling for malformed responses

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details. 