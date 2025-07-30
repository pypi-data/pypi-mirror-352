import os
from .post_recent import InstagramPostRecentCollector

def test_post_recent_collector():
    """
    Test the InstagramPostRecentCollector functionality
    """
    # Load API key from environment
    api_key = "a9de658aa1msha0eec2e239bdf16p1f37d2jsn28e948bef1b1"
    if not api_key:
        raise ValueError("RAPID_API_KEY not found in environment variables")

    # Initialize collectors for both APIs
    rocket_collector = InstagramPostRecentCollector(api_key, api="social4")

    # Test username
    user_id = "12281817"

    # Test with RocketAPI
    print("\nTesting with RocketAPI:")
    try:
        posts = rocket_collector.collect_posts_by_recent(user_id)
        if posts:
            print(f"\nFound {len(posts)} posts")
            # Print first post details
            if len(posts) > 0:
                post = posts[0]
                print("\nFirst post details:")
                print(f"Post ID: {post.get('post_id')}")
                print(f"Post Link: {post.get('post_link')}")
                print(f"Caption: {post.get('caption')}")
                print(f"Comments: {post.get('num_comment')}")
                print(f"Likes: {post.get('num_like')}")
                print(f"Views: {post.get('num_view')}")
                print(f"Shares: {post.get('num_share')}")
                print(f"Timestamp: {post.get('taken_at_timestamp')}")
                print(f"Display URL: {post.get('display_url')}")
                print(f"Region: {post.get('region')}")
                print(f"Username: {post.get('username')}")
                print(f"User ID: {post.get('user_id')}")
                print(f"Music ID: {post.get('music_id')}")
                print(f"Music Name: {post.get('music_name')}")
                print(f"Duration: {post.get('duration')}")
                print(f"Has Ecommerce: {post.get('have_ecommerce_product')}")
                print(f"Ecommerce Count: {post.get('ecommerce_product_count')}")
                print(f"Is Ecommerce Video: {post.get('is_ecommerce_video')}")
                print(f"Products: {post.get('products')}")
                print(f"Live Events: {post.get('live_events')}")
        else:
            print("No posts found")
    except Exception as e:
        print(f"Error testing RocketAPI: {e}")

    # Test with SocialAPI4
    

if __name__ == "__main__":
    test_post_recent_collector() 