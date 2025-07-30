import unittest
from facebook_collector.keywords import FacebookKeywordCollector

class TestFacebookKeywordCollector(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.cookie = "sb=O7BCZ76WW9WsEOdAYM6yzAAv; ps_l=1; ps_n=1; datr=QTctaJBjzmCzCkvauajS22xQ; locale=en_US; c_user=100011101573199; wd=1014x966; fr=154fa4M7s9nP0AYCW.AWeYnFtjJww8RUcuGjNTV2KJh08b7CDeE9WB4z6C5G2ehiVJvQs.BoLUWC..AAA.0.0.BoLUWC.AWdtSQsdF2R0FpYxBqOBjTk6Ux8; xs=25%3AfCTnO2_KnAfdyQ%3A2%3A1747793760%3A-1%3A6199%3A%3AAcVTbsaj1slav5MmvyJljnZnGyutqtT7iFsLZtbQdQ; presence=C%7B%22t3%22%3A%5B%5D%2C%22utc3%22%3A1747798418147%2C%22v%22%3A1%7D"
        self.collector = FacebookKeywordCollector(
            cookie=self.cookie,
            max_post_by_keyword=10,
            max_keyword_post_retry=2
        )

    def tearDown(self):
        """Clean up test fixtures after each test method."""
        if hasattr(self.collector, 'graphql_collector'):
            self.collector.graphql_collector.close()

    def test_collect_posts_by_keyword(self):
        """Test collecting posts by keyword."""
        posts = self.collector.collect_posts_by_keyword('test')
        print("\nCollected posts:", posts)  # Print posts for verification
        self.assertIsInstance(posts, list)


if __name__ == '__main__':
    unittest.main() 