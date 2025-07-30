import datetime
import requests
from .utils import hashtag_detect
import time
from .constant import FacebookConstants
from facebook_collector.profile_by_graphAPI import UserInfoHandler


class FacebookBrandCollector:
    """
    A class to collect Facebook posts by username using Graph API.
    """

    def __init__(self, api_key, max_post_by_brand=100, max_brand_post_retry=3):
        """
        Initialize the collector with an API key and configuration.

        Args:
            api_key (str): Your Facebook Graph API access token
            max_post_by_brand (int): Maximum number of posts to collect per brand (default: 100)
            max_brand_post_retry (int): Maximum number of retries for post collection (default: 3)
        """
        self.api_key = api_key
        self.MAX_POST_BY_BRAND = max_post_by_brand
        self.MAX_BRAND_POST_RETRY = max_brand_post_retry

    def collect_posts_by_brand(self, username):
        """
        Collect posts for a Facebook page/brand.

        Args:
            username (str): Username/page ID to collect posts for

        Returns:
            list: A list of collected posts with user info
        """
        try:

            posts, user_info = self._get_posts(username)
            print(f"Found {len(posts)} posts for user {username}")

            content_full = []
            for i in posts:
                caption = i["message"] if i["message"] is not None else ""
                create_date = datetime.datetime.strptime(i["created_time"], "%Y-%m-%dT%H:%M:%S%z").strftime(
                            "%m/%d/%Y")
                try:
                    post_info = {
                            "search_method": "Brand",
                            "input_kw_hst": username,
                            "post_id": i["id"],
                            "post_link": i["permalink_url"],
                            "caption": caption,
                            "hashtag": ", ".join(self._hashtag_detect(i["message"])) if "message" in i and i["message"] else "",
                            "hashtags": self._hashtag_detect(i["message"] if "message" in i and i["message"] else ""),
                            "created_date": create_date,
                            "num_view": int(i["view"]) if i["view"] and i["view"] != '' else -1,
                            "num_like": int(i["reactions"]["summary"]["total_count"]) if "reactions" in i and "summary" in i["reactions"] else 0,
                            "num_comment": int(i["comments"]["summary"]["total_count"]) if "comments" in i and "summary" in i["comments"] else 0,
                            "num_share": int(i["shares"]["count"]) if "shares" in i and "count" in i["shares"] else 0,
                            "num_buzz": None,
                            "num_save": None,
                            "target_country": "",
                            "user_id": i["from"]["id"],
                            "username": username,
                            "avatar_url": None,
                            "bio": user_info["bio"],
                            "num_follower": str(user_info["num_follower"]),
                            "full_name": i["from"]["name"],
                            "display_url": "",
                            "taken_at_timestamp": int(i["taken_at"]),
                            "music_id": None,
                            "music_name": None,
                            "duration": None,
                            "products": None,
                            "live_events": None,
                            "content_type": "VIDEO" if i["view"] and i["view"] != '' else "PHOTO",
                            "brand_partnership": None,
                            "user_type": None,
                        }
                    content_full.append(post_info)
                except Exception as error:
                    print(f"Error processing post: {error}")
                    continue

            return content_full

        except Exception as e:
            print(f"Error collecting posts for brand {username}: {e}")
            return []

    def _get_user_info(self, username):
        """Get user information using UserInfoHandler"""
        handler = UserInfoHandler(self.api_key)
        return handler.get_user_info(username)

    def _get_posts(self, username, time_start, time_end, max_post_by_brand=1000, country_code=None):
        """
        Get posts for a given Facebook username.

        Args:
            username (str): The Facebook username to get posts for
            time_start (str): Start date in format 'YYYY-MM-DD'
            time_end (str): End date in format 'YYYY-MM-DD'
            max_post_by_brand (int, optional): Maximum number of posts to collect. Defaults to 1000.
            country_code (str, optional): The country code to filter by

        Returns:
            tuple: A tuple containing (list of posts, user_info)
        """
        print("Getting posts for brand:", username)
        retry = 0
        collected_posts = []
        user_info = {}
        
 
        user_info = self._get_user_info(username)
        if not user_info:
            return collected_posts, user_info

        # Convert time strings to timestamps
        date_format = "%Y-%m-%d %H:%M:%S"
        time_start_ts = datetime.datetime.strptime(time_start + " 00:00:01", date_format).timestamp()
        time_end_ts = datetime.datetime.strptime(time_end + " 23:59:59", date_format).timestamp()
        print(f'Time range: {time_start} to {time_end}')

        # Initial API request
        time.sleep(1)
        url = f"https://graph.facebook.com/v20.0/{username}/posts?access_token={self.api_key}&__cppo=1&debug=all&fields=id%2Cviews%2Cwidth%2Ctargeting%2Ctarget%2Cstory_tags%2Cstory%2Cpromotable_id%2Cexpanded_width%2Cheight%2Cfeed_targeting%2Cexpanded_height%2Cfull_picture%2Cpermalink_url%2Cpicture%2Cstatus_type%2Cmessage%2Cmessage_tags%2Cshares%2Creactions.limit(0).summary(true)%2Ccomments.limit(0).summary(true)%2Cattachments%7Bdescription%2Cdescription_tags%2Cmedia%2C%20media_type%2C%20target%2C%20title%2C%20type%2Cunshimmed_url%2C%20url%7D%2Csharedposts.limit(0).summary(true)%2Ccreated_time%2Cfrom%2Cto%2Ccoordinates%2Cplace%2Cproperties%2Cupdated_time%2Cvia%2Cparent_id%2Cis_hidden&format=json&limit=30&method=get&pretty=0&suppress_http_code=1&transport=cors"

        loop_index = 1
        check_created_time = False

        while True:
            try:
                response = requests.request("GET", url, data={})
                data = response.json()
                
                for post in data["data"]:
                    date_string = post["created_time"]
                    date_format = "%Y-%m-%dT%H:%M:%S%z"
                    taken_at = datetime.datetime.strptime(date_string, date_format).timestamp()
                    post["taken_at"] = taken_at

                    if taken_at > time_end_ts:
                        continue
                    if taken_at < time_start_ts:
                        check_created_time = True
                        break

                    post["view"] = ""
                    if post["status_type"] == "added_video":
                        time.sleep(1)
                        link = post["permalink_url"].strip('/').split('/')
                        detail_post = self._get_post_info(link[-1])
                        if detail_post is not None and 'views' in detail_post:
                            post["view"] = detail_post["views"]

                    collected_posts.append(post)

                if "paging" in data and "next" in data["paging"]:
                    url = data["paging"]["next"]
                    time.sleep(1)
                else:
                    break

            except Exception as e:
                print("Error loading posts for brand:", e)
                retry += 1

            posts_count = len(collected_posts)
            print(f"Loop {loop_index} | Total posts: {posts_count}")

            # Break conditions
            if (check_created_time or 
                retry > self.MAX_BRAND_POST_RETRY or 
                posts_count > self.MAX_POST_BY_BRAND or 
                posts_count > max_post_by_brand):
                break

            loop_index += 1

        return collected_posts, user_info
    
    def _get_post_info(self, post_id):
        try:

            url = f"https://graph.facebook.com/v20.0/{post_id}?access_token={self.api_key}&debug=all&fields=views&format=json&method=get&origin_graph_explorer=1&pretty=0&suppress_http_code=1&transport=cors"
            print(url)
            response = requests.request("GET", url, data={})

            data = response.json()
            return data
        except Exception as e:
            print("Load post by brand error", e)
            return None

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


