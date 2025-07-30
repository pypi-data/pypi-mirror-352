class InstagramConstants:
    # API URLs
    RAPID_URL_COLLECT_HASHTAG_POSTS_ROCKET = "https://rocketapi-for-developers.p.rapidapi.com/instagram/hashtag/get_media"
    RAPID_URL_COLLECT_HASHTAG_POSTS_SOCIAL4 = "https://social-api4.p.rapidapi.com/v1/hashtag"
    RAPID_URL_COLLECT_TAGGED_POSTS_ROCKET = "https://rocketapi-for-developers.p.rapidapi.com/instagram/user/get_tags"
    RAPID_URL_COLLECT_TAGGED_POSTS_SOCIAL4 = "https://social-api4.p.rapidapi.com/v1/tagged"
    RAPID_URL_COLLECT_BRAND_POSTS_ROCKET = "https://rocketapi-for-developers.p.rapidapi.com/instagram/user/get_media"
    RAPID_URL_COLLECT_BRAND_POSTS_SOCIAL4 = "https://social-api4.p.rapidapi.com/v1/posts"
    RAPID_URL_COLLECT_COMMENTS_ROCKET = "https://rocketapi-for-developers.p.rapidapi.com/instagram/media/get_comments"
    RAPID_URL_COLLECT_COMMENTS_SOCIAL4 = "https://social-api4.p.rapidapi.com/v1/comments"

    # API Headers
    RAPID_IG_SCRAPER_ROCKET_HEADER = {
        "X-RapidAPI-Key": "YOUR_RAPID_API_KEY",
        "X-RapidAPI-Host": "rocketapi-for-developers.p.rapidapi.com"
    }

    RAPID_IG_SCRAPER_SOCIAL4_HEADER = {
        "X-RapidAPI-Key": "YOUR_RAPID_API_KEY",
        "X-RapidAPI-Host": "social-api4.p.rapidapi.com"
    }

    # Hashtag Paths
    RAPID_ROCKETAPI_HASHTAG_PATH = ["response", "body","sections"]
    RAPID_ROCKET_HASHTAG_CURSOR_PATH = ["response", "body", "next_max_id"]
    RAPID_ROCKET_HASHTAG_HASMORE_PATH = ["response", "body", "more_available"]

    RAPID_SOCIAL4_HASHTAG_PATH = ["data", "items"]
    RAPID_SOCIAL4_HASHTAG_CURSOR_PATH = ["pagination_token"]
    RAPID_SOCIAL4_HASHTAG_HASMORE_PATH = ["data","count"]

    # Tagged Posts Paths
    RAPID_ROCKETAPI_TAGGED_PATH = ["response", "body", "data", "user","edge_user_to_photos_of_you","edges"]
    RAPID_ROCKET_TAGGED_CURSOR_PATH = ["response", "body", "data", "user","edge_user_to_photos_of_you","page_info","end_cursor"]
    RAPID_ROCKET_TAGGED_HASMORE_PATH = ["response", "body", "data", "user","edge_user_to_photos_of_you","page_info","has_next_page"]

    RAPID_SOCIAL4_TAGGED_PATH = ["data", "items"]
    RAPID_SOCIAL4_TAGGED_CURSOR_PATH = ["pagination_token"]
    RAPID_SOCIAL4_TAGGED_HASMORE_PATH = ["data", "count"]

    # Brand Posts Paths
    RAPID_ROCKETAPI_BRAND_PATH = ["response", "body", "items"]
    RAPID_ROCKET_BRAND_CURSOR_PATH = ["response", "body", "next_max_id"]
    RAPID_ROCKET_BRAND_HASMORE_PATH = ["response", "body", "more_available"]

    RAPID_SOCIAL4_BRAND_PATH = ["data", "items"]
    RAPID_SOCIAL4_BRAND_CURSOR_PATH = ["pagination_token"]
    RAPID_SOCIAL4_BRAND_HASMORE_PATH = ["data", "count"]

    # Comment Paths
    RAPID_ROCKETAPI_COMMENT_PATH = ["response", "body", "comments"]
    RAPID_ROCKET_COMMENT_CURSOR_PATH = ["response", "body", "next_min_id"]
    RAPID_ROCKET_COMMENT_HASMORE_PATH = ["response", "body", "has_more_headload_comments"]

    RAPID_SOCIAL4_COMMENT_PATH = ["data", "items"]
    RAPID_SOCIAL4_COMMENT_CURSOR_PATH = ["pagination_token"]
    RAPID_SOCIAL4_COMMENT_HASMORE_PATH = ["data", "count"]

    # Other Constants
    POST_OVER_TIME_RANGE_LIMIT = 10
    COMMENT_OVER_TIME_RANGE_LIMIT = 10
    MAX_HASHTAG_POST_RETRY = 3
    MAX_TAGGED_POST_RETRY = 3
    MAX_BRAND_POST_RETRY = 3
    MAX_COMMENT_RETRY = 3
    RATE_LIMIT_DELAY = 2  # seconds