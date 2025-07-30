import datetime
import time
import requests
from .utils import transform_selling_product, hashtag_detect, get_id_by_shortcode
from .constants import InstagramConstants

class InstagramCommentCollector:
    """
    A class to collect Instagram post comments.
    """

    def __init__(self, api_key, api="rocketapi",
                 max_comment_by_post=100,
                 max_comment_retry=3):
        """
        Initialize the collector with configuration.

        Args:
            api_key (str): Your RapidAPI key
            api (str): API provider to use (rocketapi or social4)
            max_comment_by_post (int): Maximum number of comments to collect per post (default: 100)
            max_comment_retry (int): Maximum number of retries for comment collection (default: 3)
        """
        self.api_key = api_key
        self.api = api
        self.MAX_COMMENT_BY_POST = max_comment_by_post
        self.MAX_COMMENT_RETRY = max_comment_retry

        # Update headers with API key
        InstagramConstants.RAPID_IG_SCRAPER_ROCKET_HEADER["X-RapidAPI-Key"] = api_key
        InstagramConstants.RAPID_IG_SCRAPER_SOCIAL4_HEADER["X-RapidAPI-Key"] = api_key

    def collect_comments(self, post_id,):
        """
        Collect comments from an Instagram post.

        Args:
            post_id (str): The post ID to collect comments from
            time_request (int, optional): Timestamp to filter comments by. If None, defaults to 6 months ago.

        Returns:
            list: A list containing the collected comments
        """
        try:

            # Get raw comments
            raw_comments = self._get_comments(post_id)
            if not raw_comments:
                return []

            # Process comments
            content_full = []
            for comment in raw_comments:
                try:
                    processed_comments = self._process_comment(comment, post_id)
                    if processed_comments:
                        content_full.extend(processed_comments)
                except Exception as error:
                    print(f"Error processing comment: {error}")
                    continue

            return content_full

        except Exception as e:
            print(f"Error collecting comments for post {post_id}: {e}")
            return []

    def _get_comments(self, post_id):
        """
        Get raw comments from API.

        Args:
            post_id (str): The post ID to get comments from
            time_request (int): Timestamp to filter comments by

        Returns:
            list: A list of raw comments
        """
        print("Getting comments for post:", post_id)

        # Configure API parameters based on provider
        if self.api == "rocketapi":
            url = InstagramConstants.RAPID_URL_COLLECT_COMMENTS_ROCKET
            headers = InstagramConstants.RAPID_IG_SCRAPER_ROCKET_HEADER
            post_id = get_id_by_shortcode(post_id, self.api_key)
            params = {"id": post_id}
            cursor_param = "min_id"
            comments_path = InstagramConstants.RAPID_ROCKETAPI_COMMENT_PATH
            cursor_path = InstagramConstants.RAPID_ROCKET_COMMENT_CURSOR_PATH
            has_more_path = InstagramConstants.RAPID_ROCKET_COMMENT_HASMORE_PATH
        elif self.api == "social4":
            url = InstagramConstants.RAPID_URL_COLLECT_COMMENTS_SOCIAL4
            headers = InstagramConstants.RAPID_IG_SCRAPER_SOCIAL4_HEADER
            params = {"code_or_id_or_url": post_id}
            cursor_param = "pagination_token"
            comments_path = InstagramConstants.RAPID_SOCIAL4_COMMENT_PATH
            cursor_path = InstagramConstants.RAPID_SOCIAL4_COMMENT_CURSOR_PATH
            has_more_path = InstagramConstants.RAPID_SOCIAL4_COMMENT_HASMORE_PATH
        else:
            raise ValueError(f"Unsupported API provider: {self.api}")

        retry = 0
        collected_comments = []
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
                comments = self._get_nested_dict(data, comments_path)
                cursor = self._get_nested_dict(data, cursor_path)
                more_available = self._get_nested_dict(data, has_more_path)

                collected_comments.extend(comments)

                if not more_available or len(comments) < 1:
                    break

            except Exception as e:
                print("Load comments error:", e)
                retry += 1


            if retry > self.MAX_COMMENT_RETRY:
                break
            if len(collected_comments) > self.MAX_COMMENT_BY_POST:
                break

            print(f"Loop {loop_index} | Total comment {len(collected_comments)}")
            loop_index += 1

        return collected_comments

    def _process_comment(self, comment, post_id):
        """
        Process a raw comment into standardized format.

        Args:
            comment (dict): Raw comment data
            post_id (str): The post ID this comment belongs to

        Returns:
            list: A list of processed comment information
        """
        try:
            if self.api == "rocketapi":
                text = comment.get("text", "")
                user_id = comment.get("user", {}).get("id", "")
                username = comment.get("user", {}).get("username", "")
                created_at = comment.get("created_at")
                create_date = datetime.datetime.utcfromtimestamp(
                    created_at).strftime("%m/%d/%Y") if created_at else ""
                comment_id = comment.get("pk", "")
                like_count = comment.get("comment_like_count", 0)

                comment_info = [{
                    "comment_id": comment_id,
                    "post_id": post_id,
                    "text": text,
                    "num_like": like_count,
                    "num_reply": None,
                    "user_id": user_id,
                    "user_name": username,
                    "full_name": None,
                    "avatar_url": None,
                    "bio": None,
                    "bio_url": None,
                    "num_follower": None,
                    "num_following": None,
                    "num_post": None,
                    "youtube_channel_id": None,
                    "ins_id": user_id,
                    "live_commerce": None,
                    "region": None,
                    "create_time": datetime.datetime.fromtimestamp(
                        int(created_at) if created_at is not None else int(datetime.datetime.now().timestamp())
                    ).strftime("%Y-%m-%d %H:%M:%S")
                }]
                return comment_info

            elif self.api == "social4":
                text = comment.get("text", "")
                user_id = comment.get("user", {}).get("id", "")
                username = comment.get("user", {}).get("username", "")
                created_at = comment.get("created_at")
                create_date = datetime.datetime.utcfromtimestamp(
                    created_at).strftime("%m/%d/%Y") if created_at else ""
                comment_id = comment.get("id", "")
                like_count = comment.get("like_count", 0)

                comment_info = [{
                    "comment_id": comment_id,
                    "post_id": post_id,
                    "text": text,
                    "num_like": like_count,
                    "num_reply": None,
                    "user_id": user_id,
                    "user_name": username,
                    "full_name": None,
                    "avatar_url": None,
                    "bio": None,
                    "bio_url": None,
                    "num_follower": None,
                    "num_following": None,
                    "num_post": None,
                    "youtube_channel_id": None,
                    "ins_id": user_id,
                    "live_commerce": None,
                    "region": None,
                    "create_time": datetime.datetime.fromtimestamp(
                        int(created_at) if created_at is not None else int(datetime.datetime.now().timestamp())
                    ).strftime("%Y-%m-%d %H:%M:%S")
                }]
                return comment_info

        except Exception as e:
            print(f"Error processing comment: {e}")
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