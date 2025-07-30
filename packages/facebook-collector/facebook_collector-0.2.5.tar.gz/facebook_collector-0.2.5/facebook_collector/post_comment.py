import datetime
import json
import time
from facebook_collector.constant import FacebookConstants
from facebook_collector.graphql_handler import FacebookGraphQLCollector
from facebook_collector.utils import convert_to_number
import re


class FacebookPostCommentCollector:
    """
    A class to collect Facebook post comments using cookie authentication.
    """

    def __init__(self, cookie, max_comments, max_comment_retry):
        """
        Initialize the collector with cookie and configuration.

        Args:
            cookie (str): Facebook authentication cookie
            max_comments (int): Maximum number of comments to collect per post (default: 100)
            max_comment_retry (int): Maximum number of retries for comment collection (default: 3)
        """
        self.cookie = cookie
        self.MAX_COMMENTS = max_comments
        self.MAX_COMMENT_RETRY = max_comment_retry
        self.graphql_collector = FacebookGraphQLCollector(cookie)

    def collect_comments_by_post(self, post_url):
        """
        Collect comments for a single post.

        Args:
            post_url (str): The URL of the post to collect comments from

        Returns:
            list: A list of collected comments with their details
        """
        try:
            comments_list = self._get_comments(post_url)
            print(f"Found {len(comments_list)} comments for post {post_url}")
            return comments_list
        except Exception as e:
            print(f"Error collecting comments for post {post_url}: {e}")
            return []

    def _get_comments(self, post_url, max_comments=100):
        """
        Get comments from a post
        :param post_url: URL of the post
        :param max_comments: Maximum number of comments to collect
        :return: List of comments
        """
        comments = []
        seen_comment_ids = set()
        retry_count = 0
        
        # Navigate to post page
        self.graphql_collector.navigate_to_url(post_url)
        
        # Scroll and collect comments until we reach max_comments or no more data
        while len(comments) < self.MAX_COMMENTS and retry_count < self.MAX_COMMENT_RETRY:
            # Get GraphQL requests
            logs = self.graphql_collector.get_performance_logs()
            
            # Process each log
            for log in logs:
                try:
                    body = log['body']
                    
                    # Parse first dict
                    try:
                        start_idx = body.find('{')
                        if start_idx != -1:
                            stack = []
                            end_idx = start_idx
                            for i in range(start_idx, len(body)):
                                if body[i] == '{':
                                    stack.append(i)
                                elif body[i] == '}':
                                    if stack:
                                        stack.pop()
                                        if not stack:
                                            end_idx = i
                                            break
                            
                            first_dict = body[start_idx:end_idx + 1]
                            data = json.loads(first_dict)
                            
                            # Extract comments
                            extracted_comments = self._get_response_body(data)
                            for comment in extracted_comments:
                                comment_id = comment['comment_id']
                                if comment_id not in seen_comment_ids:
                                    seen_comment_ids.add(comment_id)
                                    comments.append(comment)
                                    
                                    if len(comments) >= self.MAX_COMMENTS:
                                        return comments
                    except Exception as e:
                        print(f"Error parsing first dict: {str(e)}")
                        retry_count += 1
                        if retry_count >= self.MAX_COMMENT_RETRY:
                            print(f"Max retries reached ({self.MAX_COMMENT_RETRY}). Stopping collection.")
                            return comments
                        continue
                except Exception as e:
                    print(f"Error processing log: {str(e)}")
                    retry_count += 1
                    if retry_count >= self.MAX_COMMENT_RETRY:
                        print(f"Max retries reached ({self.MAX_COMMENT_RETRY}). Stopping collection.")
                        return comments
                    continue
            # Scroll within the popup to load more comments
            if not self.graphql_collector.scroll_popup():
                return comments
            self.graphql_collector.scroll_popup()
            
            time.sleep(2)  # Wait for new content to load
        
        return comments

    def _get_response_body(self, response_text):
        """
        Extracts and formats comment data from the Facebook response JSON.
        """
        response_data = []
        print('-------process comments---')
        
        data = response_text.get('data') if response_text.get('data') is not None else {}
        data = data.get('node') if data.get('node') is not None else {}
        data = data.get('comment_rendering_instance_for_feed_location') if data.get('comment_rendering_instance_for_feed_location') is not None else {}
        data = data.get('comments') if data.get('comments') is not None else []
        edges = data.get('edges') if data.get('edges') is not None else []

        if len(edges) > 0:
            for edge in edges:
                node = edge.get('node') if edge.get('node') else {}
                if not node:
                    continue

                comment_id = node.get('id')
                message = node.get('body', {}).get('text') if node.get('body') else None
                created_time = node.get('comment_action_links',{}).get("comment",{}).get("created_time") if node.get('comment_action_links') else None
                taken_at = None
                taken_num = None
                
                if created_time:
                    taken_num = created_time
                    taken_at = datetime.datetime.utcfromtimestamp(created_time).strftime("%m/%d/%Y")

                # Get author information
                author = node.get('author') if node.get('author') else {}
                user_id = author.get('id')
                user_name = author.get('name')
                profile_url = author.get('url')
                username = _extract_facebook_username(profile_url) if profile_url else None

                # Get reaction counts
                reactions = node.get('reactions', {})
                like_count = reactions.get('count') if reactions else 0

                if comment_id:
                    response_data.append({
                        'comment_id': comment_id,
                        'post_id': None,
                        'text': message,
                        'num_like': None,
                        'num_reply': None,
                        'user_id': user_id,
                        'user_name': username,
                        'full_name': user_name,
                        'avatar_url': None,
                        'bio': None,
                        'bio_url': None,
                        'num_follower': None,
                        'num_following': None,
                        'num_post': None,
                        'youtube_channel_id': None,
                        'ins_id': None,
                        'live_commerce': None,
                        'region': None,
                        'create_time': taken_num
                    })

        return response_data


def _extract_facebook_username(url):
    try:
        username_regex = re.compile(r'(?:https?://)?(?:www\.)?(?:m\.)?facebook\.com/(?:profile\.php\?id=)?([\w\-\.]+)')
        match = username_regex.search(url)
        if match:
            return match.group(1)
        else:
            return None
    except:
        return None


def main():
    cookie = "sb=IYUrZjBZMwoK8Jl4_hYU8UwG; datr=No8gZ4RinbIdcPoADtWIC6FD; ps_l=1; ps_n=1; c_user=100052089082249; fr=12iPqAAVSdaNABk4P.AWcR574wPjDBArnCVSuuc6-Vq0yClEEEeBnhA7DtYXMQNvHslY0.BoNXuN..AAA.0.0.BoNXuN.AWfuDbxqvY08ocw-j0Kfy-EWyQk; xs=29%3A5hngrlHUXT2CNg%3A2%3A1740127715%3A-1%3A-1%3A%3AAcW8tV4iXwGs0HhfoWrRZcFDlqBB1-qsQkZTCx1yZMA; presence=C%7B%22t3%22%3A%5B%5D%2C%22utc3%22%3A1748335502223%2C%22v%22%3A1%7D; wd=1870x513"
    collector = FacebookPostCommentCollector(
        cookie=cookie,
        max_comments=10,
        max_comment_retry=3
    )
    
    try:
        comments = collector.collect_comments_by_post('https://web.facebook.com/dienlanhgocong/posts/pfbid02SBP5LqYLmGFpMKQTRxVgrjw8XymWBLtZz17da8tYWxY1YLEDbtpMaKxWhLi737XBl')
        print("\nCollected comments:", comments)
    finally:
        if hasattr(collector, 'graphql_collector'):
            collector.graphql_collector.close()


if __name__ == '__main__':
    main()
