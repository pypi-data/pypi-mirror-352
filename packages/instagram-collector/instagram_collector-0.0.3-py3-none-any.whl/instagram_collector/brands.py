import datetime
import time
import requests
from .utils import transform_selling_product, hashtag_detect
from .constants import InstagramConstants

class InstagramBrandCollector:
    """
    A class to collect Instagram brand information.
    """

    def __init__(self, api_key, api="rocketapi",
                 max_post_by_user=100,
                 max_brand_post_retry=3,
                 max_profile_retry=3):
        """
        Initialize the collector with configuration.

        Args:
            api_key (str): Your RapidAPI key
            api (str): API provider to use (rocketapi or social4)
            max_post_by_user (int): Maximum number of posts to collect per user (default: 100)
            max_brand_post_retry (int): Maximum number of retries for brand post collection (default: 3)
            max_profile_retry (int): Maximum number of retries for profile collection (default: 3)
        """
        self.api_key = api_key
        self.api = api
        self.MAX_POST_BY_USER = max_post_by_user
        self.MAX_BRAND_POST_RETRY = max_brand_post_retry
        self.MAX_PROFILE_RETRY = max_profile_retry

        # Update headers with API key
        InstagramConstants.RAPID_IG_SCRAPER_ROCKET_HEADER["X-RapidAPI-Key"] = api_key
        InstagramConstants.RAPID_IG_SCRAPER_SOCIAL4_HEADER["X-RapidAPI-Key"] = api_key

    def collect_brand_posts(self, user_id, time_request=None):
        """
        Collect posts from a brand's Instagram account.

        Args:
            username (str): The brand's Instagram username
            time_request (int, optional): Timestamp to filter posts by. If None, defaults to 6 months ago.

        Returns:
            list: A list containing the collected posts
        """
        try:
            if time_request is None:
                # Get current time and subtract 6 months (in seconds)
                current_time = datetime.datetime.now()
                six_months_ago = current_time - datetime.timedelta(days=180)  # Approximately 6 months
                time_request = int(six_months_ago.timestamp())

            # Get raw posts
            raw_posts = self._get_posts(user_id, time_request)
            if not raw_posts:
                return []

            # Process posts
            content_full = []
            for post in raw_posts:
                try:
                    processed_posts = self._process_post(post, user_id)
                    if processed_posts:
                        content_full.extend(processed_posts)
                except Exception as error:
                    print(f"Error processing post: {error}")
                    continue

            return content_full

        except Exception as e:
            print(f"Error collecting brand posts for {user_id}: {e}")
            return []

    def _get_posts(self, user_id, time_request):
        """
        Get raw brand posts from API.

        Args:
            username (str): The brand's Instagram username
            time_request (int): Timestamp to filter posts by

        Returns:
            list: A list of raw posts
        """

        # Configure API parameters based on provider
        if self.api == "rocketapi":
            url = InstagramConstants.RAPID_URL_COLLECT_BRAND_POSTS_ROCKET
            headers = InstagramConstants.RAPID_IG_SCRAPER_ROCKET_HEADER
            params = {"id": user_id}
            cursor_param = "max_id"
            posts_path = InstagramConstants.RAPID_ROCKETAPI_BRAND_PATH
            cursor_path = InstagramConstants.RAPID_ROCKET_BRAND_CURSOR_PATH
            has_more_path = InstagramConstants.RAPID_ROCKET_BRAND_HASMORE_PATH
        elif self.api == "social4":
            url = InstagramConstants.RAPID_URL_COLLECT_BRAND_POSTS_SOCIAL4
            headers = InstagramConstants.RAPID_IG_SCRAPER_SOCIAL4_HEADER
            params = {"username_or_id_or_url": user_id}
            cursor_param = "pagination_token"
            posts_path = InstagramConstants.RAPID_SOCIAL4_BRAND_PATH
            cursor_path = InstagramConstants.RAPID_SOCIAL4_BRAND_CURSOR_PATH
            has_more_path = InstagramConstants.RAPID_SOCIAL4_BRAND_HASMORE_PATH
        else:
            raise ValueError(f"Unsupported API provider: {self.api}")

        retry = 0
        collected_posts = []
        posts_check = 0
        cursor = None

        loop_index = 0
        while True:
            if cursor is not None:
                params[cursor_param] = cursor

            try:
                print("Request params:", params)
                if self.api == "rocketapi":
                    response = requests.post(url, headers=headers, json=params)
                elif self.api == "social4":
                    response = requests.get(url, headers=headers, params=params)

                data = response.json()
                posts = self._get_nested_dict(data, posts_path)
                cursor = self._get_nested_dict(data, cursor_path)
                more_available = self._get_nested_dict(data, has_more_path)

                # Check post timestamps
                for post in posts:
                    node = post.get("node", {})
                    taken_at = node.get("taken_at_timestamp")
                    if taken_at and taken_at < time_request:
                        posts_check += 1
                    else:
                        posts_check = 0

                collected_posts.extend(posts)

                if not more_available or len(posts) < 1:
                    break

            except Exception as e:
                print("Load brand posts error:", e)
                retry += 1

            if posts_check > InstagramConstants.POST_OVER_TIME_RANGE_LIMIT:
                break
            if retry > self.MAX_BRAND_POST_RETRY:
                break
            if len(collected_posts) > self.MAX_POST_BY_USER:
                break

            print(f"Loop {loop_index} | Total post {len(collected_posts)}")
            loop_index += 1
            time.sleep(InstagramConstants.RATE_LIMIT_DELAY)  # Rate limiting

        return collected_posts

    def _process_post(self, post, user_id):
        """
        Process a raw post into standardized format.

        Args:
            post (dict): Raw post data
            username (str): The brand's username

        Returns:
            list: A list of processed post information
        """
        try:
            if self.api == "rocketapi":
                num_like = post.get("like_count", 0)
                num_view = post.get('view_count', 0)
                user_id = post["user"]["id"]
                username = post["user"]["username"]
                num_comment = post.get("comment_count", 0)
                try:
                    caption = post["caption"].get("text")
                except:
                    caption = post.get("accessibility_caption")
                taken_at_timestamp = post.get("taken_at_timestamp")
                create_date = datetime.datetime.utcfromtimestamp(
                    taken_at_timestamp).strftime("%m/%d/%Y") if taken_at_timestamp else ""
                shortcode = post.get("code")
                post_id = post.get("pk", "")
                display_url = post.get("display_uri", "")

                post_info = [{
                    "search_method": "Brand",
                    "input_kw_hst": username,
                    "post_id": shortcode,
                    "post_link": f"www.instagram.com/p/{shortcode}",
                    "caption": caption,
                    "hashtag": ", ".join(self._hashtag_detect(caption)) if caption else "",
                    "hashtags": self._hashtag_detect(caption) if caption else [],
                    "created_date": create_date,
                    "num_view": num_view if num_view else 0,
                    "num_like": num_like if num_like else 0,
                    "num_comment": num_comment if num_comment else 0,
                    "num_share": 0,
                    "num_buzz": 0,
                    "num_save": 0,
                    "target_country": "",
                    "user_id": user_id,
                    "username": username,
                    "bio": "",
                    "full_name": username,
                    "avatar_url": "",
                    "id": post_id,
                    "display_url": display_url,
                    "taken_at_timestamp": int(taken_at_timestamp) if taken_at_timestamp is not None else int(
                        datetime.datetime.now().timestamp()),
                    "music_id": "",
                    "music_name": "",
                    "duration": 0,
                    "products": [],
                    "live_events": [],
                    "content_type": "",
                    "brand_partnership": 1,
                    "user_type": ""
                }]
                return post_info

            elif self.api == "social4":
                num_like = post.get("like_count", 0)
                num_view = post.get('view_count', 0)
                user_id = post["user"]["id"]
                username = post["user"]["username"]
                num_comment = post.get("comment_count", 0)
                try:
                    caption = post["caption"].get("text")
                except:
                    caption = post.get("accessibility_caption")
                taken_at_timestamp = post.get("taken_at_timestamp")
                create_date = datetime.datetime.utcfromtimestamp(
                    taken_at_timestamp).strftime("%m/%d/%Y") if taken_at_timestamp else ""
                shortcode = post.get("code")
                post_id = post.get("pk", "")
                display_url = post.get("display_uri", "")

                post_info = [{
                    "search_method": "Brand",
                    "input_kw_hst": username,
                    "post_id": shortcode,
                    "post_link": f"www.instagram.com/p/{shortcode}",
                    "caption": caption,
                    "hashtag": ", ".join(self._hashtag_detect(caption)) if caption else "",
                    "hashtags": self._hashtag_detect(caption) if caption else [],
                    "created_date": create_date,
                    "num_view": num_view if num_view else 0,
                    "num_like": num_like if num_like else 0,
                    "num_comment": num_comment if num_comment else 0,
                    "num_share": 0,
                    "num_buzz": 0,
                    "num_save": 0,
                    "target_country": "",
                    "user_id": user_id,
                    "username": username,
                    "bio": "",
                    "full_name": username,
                    "avatar_url": "",
                    "id": post_id,
                    "display_url": display_url,
                    "taken_at_timestamp": int(taken_at_timestamp) if taken_at_timestamp is not None else int(
                        datetime.datetime.now().timestamp()),
                    "music_id": "",
                    "music_name": "",
                    "duration": 0,
                    "products": [],
                    "live_events": [],
                    "content_type": "",
                    "brand_partnership": 1,
                    "user_type": ""
                }]
                return post_info

        except Exception as e:
            print(f"Error processing post: {e}")
            return []

    @staticmethod
    def _get_nested_dict(data, path):
        """
        Get value from nested dictionary using path.

        Args:
            data (dict): Dictionary to search in
            path (list): List of keys to traverse

        Returns:
            any: Value found or None
        """
        current = data
        for key in path:
            if isinstance(current, dict) and key in current:
                current = current[key]
            else:
                return None
        return current

    @staticmethod
    def _hashtag_detect(text):
        """
        Detect hashtags in a text.

        Args:
            text (str): The text to detect hashtags in

        Returns:
            list: A list of hashtags
        """
        return hashtag_detect(text) 