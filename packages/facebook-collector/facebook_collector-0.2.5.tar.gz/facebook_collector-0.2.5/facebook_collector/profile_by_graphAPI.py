from facebook_collector.constant import FacebookConstants
import requests


class UserInfoHandler():

    API_USER_INFO = "https://graph.facebook.com/v12.0/{username}/"
    def __init__(self, api_key):
        """
        Initialize the collector with an API key and configuration.

        Args:
            api_key (str): Your RapidAPI key for TikTok API
            country_code (str): The country code to filter posts by (default: "US")
            max_post_by_hashtag (int): Maximum number of posts to collect per hashtag (default: 100)
            max_hashtag_post_retry (int): Maximum number of retries for hashtag post collection (default: 3)
            max_profile_retry (int): Maximum number of retries for profile collection (default: 3)
        """
        self.api_key = api_key

    def get_user_info(self, username):
        url = self.API_USER_INFO.format(username=username)
        collected_data = {
            "user_id": id,
            "username": username,
            "not_found": True
        }
        post_data = None
        while True:
            try:
                response = requests.get(url, params={'access_token': self.api_key, 'fields': FacebookConstants.PROFILE_QUERY_FIELDS})

                data = response.json()
                if data:
                    collected_data = self.format_data_user(data)

                    posts = self._transform_posts(collected_data,
                                                  data.get("posts", {}).get('data', []),
                                                  data.get("videos", {}).get('data', []))
                    latest_posts = [str(item.get("_id")) for item in posts]
                    latest_post_at = posts[0].get("taken_at_timestamp")
                    post_data = dict(
                        posts=posts,
                        latest_post_at=latest_post_at,
                        latest_posts=latest_posts
                    )
                    collected_data["post_data"] = post_data
                break
            except Exception as e:
                print("Load profile error", e)
                break
        return collected_data

