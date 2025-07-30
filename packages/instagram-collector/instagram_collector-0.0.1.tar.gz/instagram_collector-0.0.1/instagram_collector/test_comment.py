from .comments import InstagramCommentCollector

def test_comment_collector():
    """
    Test the Instagram comment collector functionality.
    """
    # Initialize collector with your API key
    api_key = "YOUR_RAPID_API_KEY"
    collector = InstagramCommentCollector(api_key=api_key, api="rocketapi")

    # Test with a post ID
    post_id = "C5YwX5QNQYw"  # Example post ID
    comments = collector.collect_comments(post_id)

    # Print results
    print(f"\nFound {len(comments)} comments for post {post_id}")
    for comment in comments:
        print("\nComment Details:")
        print(f"ID: {comment.get('comment_id')}")
        print(f"Text: {comment.get('text')}")
        print(f"Created Date: {comment.get('created_date')}")
        print(f"Username: {comment.get('username')}")
        print(f"Likes: {comment.get('like_count')}")
        print(f"Hashtags: {comment.get('hashtags')}")

if __name__ == "__main__":
    test_comment_collector() 