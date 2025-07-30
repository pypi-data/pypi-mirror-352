import datetime
import json
import time
import requests
from .constants import InstagramConstants
from instagram_collector.core.dynamodb import DynamoDB
from instagram_collector.core.dynamo_helper import DynamoHelper

class InstagramProfileCollector:
    """
    A class to collect Instagram user profile information.
    """

    def __init__(self, api_key, api="rocketapi", max_retry=3):
        """
        Initialize the collector with configuration.

        Args:
            api_key (str): Your RapidAPI key    
            api (str): API provider to use (rocketapi or social4)
            max_retry (int): Maximum number of retries for profile collection (default: 3)
        """
        self.api_key = api_key
        self.api = api
        self.MAX_RETRY = max_retry
        self.graph_over_quota = False
        self.quota_check_time = 0
        self.remain_quota = 0
        self.graph_accounts = self._load_graph_token()

        # Update headers with API key
        InstagramConstants.RAPID_IG_SCRAPER_ROCKET_HEADER["X-RapidAPI-Key"] = api_key
        InstagramConstants.RAPID_IG_SCRAPER_SOCIAL4_HEADER["X-RapidAPI-Key"] = api_key

    def _load_graph_token(self):
        """
        Load Graph API tokens from DynamoDB.

        Returns:
            list: List of available Graph API tokens
        """
        try:
            key_data = DynamoHelper.serialize({
                "PK": "instagram_graph_api_token"
            })

            dynamo_table = "production-influencer"
            dynamo = DynamoDB()

            key_condition_expression, attribute_values, attribute_names = DynamoHelper.get_query_params(
                key_data=key_data,
                begin_with_fields=["SK"]
            )
            
            items = dynamo.query_with(
                dynamo_table,
                key_condition_expression,
                attribute_values,
                attribute_names
            )

            deserialized_items = []
            for item in items:
                deserialized_item = DynamoHelper.deserialize(item)
                if (deserialized_item.get("token_status") == "available" and 
                    deserialized_item.get("access_token") and 
                    deserialized_item.get("instagram_id")):
                    deserialized_items.append(deserialized_item)

            return deserialized_items
        except Exception as e:
            print(f"Error loading Graph API tokens: {e}")
            return []

    def get_additional(self, username):
        """
        Get additional profile information including location.

        Args:
            user_id (str): The Instagram user ID

        Returns:
            str: Location information
        """
        url = "https://social-api4.p.rapidapi.com/v1/info_about"
        headers = InstagramConstants.RAPID_IG_SCRAPER_SOCIAL4_HEADER
        params = {"username_or_id_or_url": username}

        retry = 0
        account_location = ""
        while retry < self.MAX_RETRY:
            try:
                response = requests.get(url, headers=headers, params=params)
                data = response.json()

                if data.get("data", {}).get("country"):
                    account_location = data.get("data", {}).get("country", "")
                    break
            except Exception as e:
                print(f"Error getting additional info: {e}")
            time.sleep(2)
            retry += 1

        return account_location

    def collect_profile(self, username, user_id=None, get_additional=False):
        """
        Collect profile information for a given username.

        Args:
            username (str): The Instagram username to collect profile for
            user_id (str, optional): The Instagram user ID
            get_additional (bool): Whether to fetch additional information like location

        Returns:
            tuple: (profile_data, posts_data)
        """
        try:
            # Try Graph API first if not over quota
            if not self.graph_over_quota:
                data = self._get_by_graph_api(username)
                if data:
                    profile_data = self._process_graph_profile(data)
                    posts_data = self._process_graph_posts(data.get("media", {}).get("data", []))
                    
                    if get_additional and profile_data:
                        location = self.get_additional(profile_data["id"])
                        if location:
                            profile_data["account_location"] = location
                            profile_data["home_country"] = location
                    
                    return profile_data, posts_data

            # Fallback to RapidAPI if Graph API fails or over quota
            if self.api == "rocketapi":
                url = "https://rocketapi-for-developers.p.rapidapi.com/instagram/user/get_info"
                headers = InstagramConstants.RAPID_IG_SCRAPER_ROCKET_HEADER
                params = {"username": username}
                response = requests.post(url, json=params, headers=headers)
            elif self.api == "social4":
                url = "https://social-api4.p.rapidapi.com/v1/info"
                headers = InstagramConstants.RAPID_IG_SCRAPER_SOCIAL4_HEADER
                params = {"username_or_id_or_url": username}
                response = requests.get(url, params=params, headers=headers)
            else:
                raise ValueError(f"Unsupported API provider: {self.api}")

            data = response.json()
            profile_data = self._process_profile(data)
            
            if get_additional and profile_data:
                location = self.get_additional(profile_data["id"])
                if location:
                    profile_data["account_location"] = location
                    profile_data["home_country"] = location
            
            return profile_data, None

        except Exception as e:
            print(f"Error collecting profile for username {username}: {e}")
            return None, None

    def _get_by_graph_api(self, username):
        """
        Get profile data using Graph API.

        Args:
            username (str): The Instagram username

        Returns:
            dict: Raw profile data from Graph API
        """
        try:
            # Get available token
            graph_account = next(
                (account for account in self.graph_accounts if account.get("token_status") == "available"),
                None
            )
            
            if not graph_account:
                print("No available Graph API tokens")
                return None

            url = f"https://graph.facebook.com/v18.0/{graph_account.get('instagram_id')}"
            params = {
                'access_token': graph_account.get("access_token"),
                'fields': f'business_discovery.username({username}){{id,username,name,profile_picture_url,biography,followers_count,follows_count,media_count,website,media{{id,caption,media_type,media_url,thumbnail_url,permalink,timestamp,like_count,comments_count,media_product_type}}}}'
            }

            response = requests.get(url, params=params)
            data = response.json()

            # Check quota
            quota_info = response.headers.get("x-app-usage")
            if quota_info:
                quota_info = json.loads(quota_info)
                if quota_info.get("call_count") > 80 or quota_info.get("total_time") > 80:
                    print("Graph API over quota")
                    self.graph_over_quota = True
                    self.quota_check_time = int(datetime.datetime.now().timestamp())
                self.remain_quota = quota_info.get("total_time")

            return data.get('business_discovery')

        except Exception as e:
            print(f"Error getting profile from Graph API: {e}")
            return None

    def _process_graph_profile(self, data):
        """
        Process raw profile data from Graph API into standardized format.

        Args:
            data (dict): Raw profile data from Graph API

        Returns:
            dict: Processed profile information
        """
        try:
            return {
                "id": str(data.get("id", "")),
                "username": data.get("username", ""),
                "full_name": data.get("name", ""),
                "biography": data.get("biography", ""),
                "followers_count": data.get("followers_count", 0),
                "following_count": data.get("follows_count", 0),
                "media_count": data.get("media_count", 0),
                "is_private": False,
                "is_verified": False,
                "profile_pic_url": data.get("profile_picture_url", ""),
                "external_url": data.get("website", "")
            }
        except Exception as e:
            print(f"Error processing Graph API profile data: {e}")
            return None

    def _process_graph_posts(self, posts):
        """
        Process raw posts data from Graph API into standardized format.

        Args:
            posts (list): List of raw post data from Graph API

        Returns:
            list: List of processed posts
        """
        try:
            processed_posts = []
            for post in posts:
                hiip_post_type = 'photo'
                if post.get("media_type") == "VIDEO":
                    hiip_post_type = 'video'
                    display_url = post.get("thumbnail_url")
                    if post.get("media_product_type") == "REELS":
                        hiip_post_type = "reels"
                else:
                    display_url = post.get("media_url")

                processed_post = {
                    "_id": post.get("id"),
                    "content": post.get("caption"),
                    "num_like": post.get("like_count", 0),
                    "num_liked_by": post.get("like_count", 0),
                    "num_reaction": post.get("like_count", 0),
                    "num_comment": post.get("comments_count", 0),
                    "shortcode": post.get("permalink", "").strip("/").split("/")[-1],
                    "post_type": post.get("media_type"),
                    "product_type": post.get("media_product_type"),
                    "hiip_post_type": hiip_post_type,
                    "taken_at_timestamp": int(
                        datetime.datetime.strptime(
                            post.get("timestamp", "").split("+")[0], 
                            "%Y-%m-%dT%H:%M:%S"
                        ).timestamp()
                    ) if post.get("timestamp") else 0,
                    "display_url": display_url
                }
                processed_posts.append(processed_post)

            # Sort posts by timestamp in descending order
            processed_posts.sort(key=lambda x: x["taken_at_timestamp"], reverse=True)
            return processed_posts

        except Exception as e:
            print(f"Error processing Graph API posts data: {e}")
            return []

    def _process_profile(self, data):
        """
        Process raw profile data from RapidAPI into standardized format.

        Args:
            data (dict): Raw profile data from API

        Returns:
            dict: Processed profile information
        """
        try:
            if self.api == "rocketapi":
                user = data.get("response", {}).get("body", {}).get("data", {}).get("user", {})
                return {
                    "id": user.get("id", ""),
                    "username": user.get("username", ""),
                    "full_name": user.get("full_name", ""),
                    "biography": user.get("biography", ""),
                    "followers_count": user.get("edge_followed_by", {}).get("count", 0),
                    "following_count": user.get("edge_follow", {}).get("count", 0),
                    "media_count": user.get("edge_owner_to_timeline_media", {}).get("count", 0),
                    "is_private": user.get("is_private", False),
                    "is_verified": user.get("is_verified", False),
                    "profile_pic_url": user.get("profile_pic_url", ""),
                    "external_url": user.get("external_url", "")
                }
            elif self.api == "social4":
                user = data.get("data", {})
                return {
                    "id": user.get("id", ""),
                    "username": user.get("username", ""),
                    "full_name": user.get("full_name", ""),
                    "biography": user.get("biography", ""),
                    "followers_count": user.get("follower_count", 0),
                    "following_count": user.get("following_count", 0),
                    "media_count": user.get("media_count", 0),
                    "is_private": user.get("is_private", False),
                    "is_verified": user.get("is_verified", False),
                    "profile_pic_url": user.get("profile_pic_url", ""),
                    "external_url": user.get("external_url", "")
                }
            return None

        except Exception as e:
            print(f"Error processing profile data: {e}")
            return None
