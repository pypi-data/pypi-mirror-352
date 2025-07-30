from selenium.webdriver.support.ui import WebDriverWait
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support import expected_conditions as EC
import time
import json
import os
import platform
from webdriver_manager.core.os_manager import ChromeType

class FacebookGraphQLCollector:
    def __init__(self, cookie):
        """
        Initialize the collector with cookie and setup Chrome driver.
        """
        self.cookie = cookie
        self.driver = None
        self.setup_driver()
        self.request_ids = {}  # Store request IDs to match with responses

    def setup_driver(self):
        """
        Setup Chrome driver with appropriate options and cookie.
        """
        try:

            chrome_options = Options()
            # chrome_options.add_argument('--headless')
            chrome_options.set_capability(
                "goog:loggingPrefs", {
                    "performance": "ALL",
                    "browser": "ALL",
                    "network": "ALL"
                }
            )
            prefs = {
                "profile.default_content_setting_values.notifications": 2  # 1: allow, 2: block
            }
            # chrome_options.add_experimental_option("prefs", prefs)
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--disable-extensions')
            chrome_options.add_argument('--disable-software-rasterizer')

            # Configure ChromeDriver installation
            driver_path = ChromeDriverManager().install()

            # Find the actual chromedriver executable
            driver_dir = os.path.dirname(driver_path)
            if platform.system() == "Linux":
                chromedriver_path = os.path.join(driver_dir, "chromedriver")
            elif platform.system() == "Windows":
                chromedriver_path = os.path.join(driver_dir, "chromedriver.exe")
            else:
                chromedriver_path = os.path.join(driver_dir, "chromedriver")

            # Ensure driver has execute permissions
            if platform.system() != "Windows":
                os.chmod(chromedriver_path, 0o755)


            service = Service(chromedriver_path)
            self.driver = webdriver.Chrome(service=service, options=chrome_options)

            # Set cookie
            self.driver.get("https://www.facebook.com")
            cookie_dict = self._parse_cookie(self.cookie)
            for name, value in cookie_dict.items():
                self.driver.add_cookie({'name': name, 'value': value})

            # Enable performance logging
            self.driver.execute_cdp_cmd('Performance.enable', {})
            self.driver.execute_cdp_cmd('Network.enable', {})

            # Initialize request tracking
            self.request_ids = {}
        except Exception as e:
            print(f"Error setting up Chrome driver: {e}")
            if self.driver:
                self.driver.quit()
            raise e

    def _parse_cookie(self, cookie_string):
        """
        Parse cookie string into dictionary.
        """
        cookie_dict = {}
        for item in cookie_string.split(';'):
            if '=' in item:
                name, value = item.strip().split('=', 1)
                cookie_dict[name] = value
        return cookie_dict

    def parse_cookies(self, cookie_string):
        """
        Parse a cookie string into individual cookies
        :param cookie_string: String containing multiple cookies separated by semicolons
        :return: List of cookie dictionaries
        """
        cookies = []
        cookie_pairs = cookie_string.split(';')
        
        for pair in cookie_pairs:
            if '=' in pair:
                name, value = pair.strip().split('=', 1)
                cookies.append({
                    'name': name,
                    'value': value,
                    'domain': '.facebook.com'
                })
        return cookies

    def load_cookies(self, cookie_string):
        """
        Load cookies into the browser
        :param cookie_string: List of cookie dictionaries or a cookie string
        """
        # First visit Facebook to set domain
        self.driver.get('https://www.facebook.com')
        time.sleep(2)
        
        # If cookies is a string, parse it
        if isinstance(cookie_string, str):
            cookies = self.parse_cookies(cookie_string)
        else:
            cookies = cookie_string
        
        # Add each cookie
        for cookie in cookies:
            try:
                self.driver.add_cookie(cookie)
            except Exception as e:
                print(f"Error adding cookie: {str(e)}")
        
        # Refresh page to apply cookies
        self.driver.refresh()
        time.sleep(5)

    def navigate_to_url(self, url):
        """
        Navigate to a specific URL and scroll for 5 seconds to load initial content
        :param url: URL to navigate to
        """
        # # Clear existing logs
        # self.driver.execute_cdp_cmd('Network.clearBrowserCache', {})
        # self.driver.execute_cdp_cmd('Network.clearBrowserCookies', {})
        # self.request_ids.clear()
        
        # Navigate to URL
        self.driver.get(url)
        time.sleep(3)  # Wait for page load
        
        # Scroll for 5 seconds to load more content
        start_time = time.time()
        while time.time() - start_time < 5:
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(1)  # Wait 1 second between scrolls

    def get_performance_logs(self):
        """
        Get GraphQL requests from network tab
        :return: List of GraphQL requests with their responses
        """
        graphql_requests = []
        
        try:
            # Get network logs
            logs = self.driver.get_log('performance')
            # print("Number of logs received:", len(logs))
            
            for entry in logs:
                try:
                    log = json.loads(entry["message"])["message"]
                    if log["method"] == "Network.responseReceived":
                        url = log["params"]["response"]["url"]
                        if "graphql" in url:
                            request_id = log["params"]["requestId"]
                            
                            # Lấy response body
                            resp_body = self.driver.execute_cdp_cmd("Network.getResponseBody", {
                                "requestId": request_id
                            })
                            body = resp_body["body"]
                            if '{"data":{"serpResponse":{"results":{"edges":[{"node":{"role":"TOP_PUBLIC_POSTS"' in body:
                                graphql_requests.append({"url": url, "body": body}) #post by keyword
                            if '{"data":{"topic_deep_dive":' in body:
                                graphql_requests.append({"url": url, "body": body}) #post by hashtag
                            if '{"data":{"node":{"__typename":"Feedback","comment_rendering_instance_for_feed_location' in body:
                                graphql_requests.append({"url": url, "body": body}) #comment
                except Exception as e:
                    print(f"Error processing log entry: {str(e)}")
                    continue
        except Exception as e:
            print(f"Error getting performance logs: {str(e)}")
        
        return graphql_requests

    def parse_graphql_data(self):
        """
        Parse GraphQL data from Facebook using provided cookies
        :return: Dictionary of GraphQL requests with their responses, keyed by request URL
        """
        if not self.cookie:
            raise ValueError("Cookie string is required. Please set it during initialization or use set_cookie() method.")
        
        # Get GraphQL requests
        graphql_requests = self.get_performance_logs()
        
        # Convert list to dictionary with URL as key
        graphql_dict = {}
        for request in graphql_requests:
            url = request['url']
            graphql_dict[url] = {
                'body': request['body']
            }
        
        return graphql_dict

    def set_cookie(self, cookie_string):
        """
        Set or update the cookie string
        :param cookie_string: String containing Facebook cookies
        """
        self.cookie = cookie_string
        if self.driver:
            self.load_cookies(cookie_string)

    def close(self):
        if self.driver:
            self.driver.quit()

    def scroll_page(self, duration=2):
        """
        Scroll the page to load more content
        :param duration: Time to wait after scrolling in seconds
        """
        last_height = self.driver.execute_script("return document.body.scrollHeight")
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        new_height = self.driver.execute_script("return document.body.scrollHeight")
        time.sleep(duration)
        if new_height == last_height:
            return False
        return True

    def scroll_popup(self, popup_selector="div[role='dialog']", scroll_position=0, smooth_scroll=True):
        """
        Scroll within the post detail popup to load more comments
        :param popup_selector: CSS selector for the popup
        :param scroll_position: Position to scroll to
        :param smooth_scroll: Whether to use smooth scrolling
        :return: True if scroll was successful, False otherwise
        """
        # try:
            # Wait for popup to appear
        time.sleep(3)
        
        # Find the popup using multiple selectors
        popup = None
        selectors = [
            "div[role='dialog']",  # Standard dialog role
            "div.x1n2onr6.x1vjfegm",  # Facebook's popup class
            "div.x78zum5.xdt5ytf.x1iyjqo2",  # Facebook's container class
            "div.x1n2onr6.x1vjfegm.x1q0g3np.x78zum5.xdt5ytf.x1iyjqo2.xs83m0k.xeuugli.x1iyjqo2.x6ikm8r.x10wlt62.x1n2onr6"  # Full Facebook popup class
        ]
        
        for selector in selectors:
            try:
                popup = self.driver.find_element(By.CSS_SELECTOR, selector)
                if popup:
                    print(f"Found popup with selector: {selector}")
                    break
            except:
                continue
        
        if not popup:
            print("Popup element not found!")
            return False
        
        # Get initial scroll height
        initial_height = self.driver.execute_script("return arguments[0].scrollHeight", popup)
        print(f"Initial scroll height: {initial_height}")
        
        # Try multiple scroll methods
        scroll_methods = [
            # Method 1: Scroll to bottom
            """
            arguments[0].scrollTo(0, arguments[0].scrollHeight);
            """,
            
            # Method 2: Scroll with offset
            """
            arguments[0].scrollTo(0, arguments[0].scrollHeight + 500);
            """,
            
            # Method 3: Smooth scroll
            """
            arguments[0].scrollTo({
                top: arguments[0].scrollHeight,
                behavior: 'smooth'
            });
            """,
            
            # Method 4: Direct scrollTop assignment
            """
            arguments[0].scrollTop = arguments[0].scrollHeight;
            """
        ]
        
        # Try each scroll method
        for i, scroll_method in enumerate(scroll_methods, 1):
            try:
                print(f"Trying scroll method {i}")
                self.driver.execute_script(scroll_method, popup)
                time.sleep(1)  # Wait between scrolls
            except Exception as e:
                print(f"Error with scroll method {i}: {str(e)}")
                continue
        
        # Wait for content to load
        time.sleep(2)
        
        # Get final scroll height
        final_height = self.driver.execute_script("return arguments[0].scrollHeight", popup)
        print(f"Final scroll height: {final_height}")
        
        # Check if scroll was successful
        if final_height > initial_height:
            print("Scroll successful - new content loaded")
            return True
        else:
            print("Scroll did not load new content")
            return False
                
        # except Exception as e:
        #     print(f"Error scrolling popup: {str(e)}")
        #     return False

# def main():
#     # Cookie string from browser
#     cookie_string = 'sb=O7BCZ76WW9WsEOdAYM6yzAAv; ps_l=1; ps_n=1; datr=QTctaJBjzmCzCkvauajS22xQ; locale=en_US; c_user=100011101573199; wd=1014x966; fr=154fa4M7s9nP0AYCW.AWeYnFtjJww8RUcuGjNTV2KJh08b7CDeE9WB4z6C5G2ehiVJvQs.BoLUWC..AAA.0.0.BoLUWC.AWdtSQsdF2R0FpYxBqOBjTk6Ux8; xs=25%3AfCTnO2_KnAfdyQ%3A2%3A1747793760%3A-1%3A6199%3A%3AAcVTbsaj1slav5MmvyJljnZnGyutqtT7iFsLZtbQdQ; presence=C%7B%22t3%22%3A%5B%5D%2C%22utc3%22%3A1747798418147%2C%22v%22%3A1%7D'
    
#     # Initialize collector with cookie
#     collector = FacebookGraphQLCollector(cookie_string)
    
#     # Parse GraphQL data
#     graphql_dict = collector.parse_graphql_data()
    
#     collector.close()

# if __name__ == "__main__":
#     main()
