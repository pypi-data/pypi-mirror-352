import unittest
from facebook_collector.keywords import FacebookKeywordCollector


def main():
    cookie = "sb=O7BCZ76WW9WsEOdAYM6yzAAv; ps_l=1; ps_n=1; datr=QTctaJBjzmCzCkvauajS22xQ; locale=en_US; c_user=100011101573199; wd=1014x966; fr=154fa4M7s9nP0AYCW.AWeYnFtjJww8RUcuGjNTV2KJh08b7CDeE9WB4z6C5G2ehiVJvQs.BoLUWC..AAA.0.0.BoLUWC.AWdtSQsdF2R0FpYxBqOBjTk6Ux8; xs=25%3AfCTnO2_KnAfdyQ%3A2%3A1747793760%3A-1%3A6199%3A%3AAcVTbsaj1slav5MmvyJljnZnGyutqtT7iFsLZtbQdQ; presence=C%7B%22t3%22%3A%5B%5D%2C%22utc3%22%3A1747798418147%2C%22v%22%3A1%7D"
    collector = FacebookKeywordCollector(
        cookie=cookie,
        max_post_by_keyword=10,
        max_keyword_post_retry=2
    )
    
    try:
        posts = collector.collect_posts_by_keyword('test')
        print("\nCollected posts:", posts)
    finally:
        if hasattr(collector, 'graphql_collector'):
            collector.graphql_collector.close()


if __name__ == '__main__':
    main() 