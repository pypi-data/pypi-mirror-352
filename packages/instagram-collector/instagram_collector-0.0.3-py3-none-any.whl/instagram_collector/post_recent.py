import datetime
import requests
import time
from .utils import transform_selling_product, hashtag_detect
from .constants import InstagramConstants

class InstagramPostRecentCollector:
    """
    A class to collect Instagram recent posts.
    """

    def __init__(self, api_key, api="social4"):
        """
        Initialize the collector with configuration.

        Args:
            api_key (str): Your RapidAPI key
            api (str): API provider to use (rocketapi or social4)
        """
        self.api_key = api_key
        self.api = api

        # Update headers with API key
        InstagramConstants.RAPID_IG_SCRAPER_ROCKET_HEADER["X-RapidAPI-Key"] = api_key
        InstagramConstants.RAPID_IG_SCRAPER_SOCIAL4_HEADER["X-RapidAPI-Key"] = api_key

    def collect_posts_by_recent(self, user_id):
        """
        Collect recent posts from a user's Instagram account.

        Args:
            user_id (str): The user ID to collect posts for

        Returns:
            list: A list containing the collected posts
        """
        try:
            content_list = self._get_posts(user_id)
            print(f"Found {len(content_list)} posts for user {user_id}")

            content_full = []
            for post in content_list:
                try:
                    processed_post = self._process_post(post)
                    if processed_post:
                        content_full.append(processed_post)
                except Exception as error:
                    print(f"Error processing post: {error}")
                    continue

            return content_full

        except Exception as e:
            print(f"Error collecting posts for user {user_id}: {e}")
            return []

    def _get_posts(self, user_id):
        """
        Get raw posts from API.

        Args:
            user_id (str): The user ID to get posts for

        Returns:
            list: A list of raw posts (limited to 30 posts)
        """
        print(f"Getting posts for user_id {user_id}")

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
        cursor = None

        loop_index = 0
        while len(collected_posts) < 30:  # Only collect up to 30 posts
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

                # Only add posts until we reach 30
                remaining_posts = 30 - len(collected_posts)
                posts_to_add = posts[:remaining_posts]
                collected_posts.extend(posts_to_add)

                if not more_available or len(posts) < 1 or len(collected_posts) >= 30:
                    break

            except Exception as e:
                print("Load posts error:", e)
                retry += 1

            if retry > 3:
                break

            print(f"Loop {loop_index} | Total post {len(collected_posts)}")
            loop_index += 1

        return collected_posts

    def _process_post(self, post):
        """
        Process a raw post into standardized format.

        Args:
            post (dict): Raw post data

        Returns:
            dict: Processed post information
        """
        try:
            if self.api == "rocketapi":
                caption = post.get("caption", {}).get("text", "")
                taken_at_timestamp = post.get("taken_at_timestamp")
                user_data = post.get("user", {})
                image_data = post.get("image_versions2", {}).get("candidates", [])
                products = post.get("products", [])
                live_events = post.get("live_events", [])
                is_ecommerce_video = post.get("is_ecommerce_video", False)

                return {
                    "post_id": post.get("id", "").split("_")[0] if post.get("id") else "",
                    "post_link": f"www.instagram.com/p/{post.get('code')}",
                    "caption": caption,
                    "num_comment": post.get("comment_count", 0),
                    "num_like": post.get("like_count", 0),
                    "num_view": post.get("play_count", 0),
                    "num_share": 0,
                    "taken_at_timestamp": int(taken_at_timestamp) if taken_at_timestamp else 0,
                    "display_url": image_data[2].get("url") if len(image_data) > 2 else image_data[-1].get("url") if image_data else "",
                    "region": "",
                    "username": user_data.get("username"),
                    "user_id": user_data.get("id"),
                    "music_id": post.get("music", {}).get("id", ""),
                    "music_name": post.get("music", {}).get("title", ""),
                    "duration": float(post.get("duration", 0)),
                    "have_ecommerce_product": True if len(products) > 0 else False,
                    "ecommerce_product_count": len(products),
                    "is_ecommerce_video": is_ecommerce_video,
                    "products": products,
                    "live_events": live_events
                }

            elif self.api == "social4":
                caption = post.get("caption", {}).get("text", "")
                taken_at_timestamp = post.get("taken_at_timestamp")
                products = post.get("products", [])
                live_events = post.get("live_events", [])
                is_ecommerce_video = post.get("is_ecommerce_video", False)

                return {
                    "post_id": post.get("id"),
                    "post_link": f"www.instagram.com/p/{post.get('code')}",
                    "caption": caption,
                    "num_comment": post.get("comment_count", 0),
                    "num_like": post.get("like_count", 0),
                    "num_view": post.get("play_count", 0),
                    "num_share": 0,
                    "taken_at_timestamp": int(taken_at_timestamp) if taken_at_timestamp else 0,
                    "display_url": post.get("thumbnail_url"),
                    "region": "",
                    "username": post.get("user", {}).get("username"),
                    "user_id": post.get("user", {}).get("id"),
                    "music_id": "",
                    "music_name": "",
                    "duration": float(post.get("duration", 0)),
                    "have_ecommerce_product": True if len(products) > 0 else False,
                    "ecommerce_product_count": len(products),
                    "is_ecommerce_video": is_ecommerce_video,
                    "products": products,
                    "live_events": live_events
                }

        except Exception as e:
            print(f"Error processing post: {e}")
            return None

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
