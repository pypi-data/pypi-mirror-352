import json
import re


def transform_selling_product(data) -> list:
    """
    Transform selling product data from TikTok API response.

    Args:
        data (dict): The product data from the API response

    Returns:
        list: A list of transformed product information
    """
    product_list = []
    if extra := data.get('extra', None):
        for product in json.loads(extra):
            product_info = json.loads(product['extra'])
            _id = product_info.get('product_id', None)
            product_name = product_info.get('title', None)
            thumbnail = product_info.get('cover_url', None)
            seller_id = product_info.get('seller_id', None)
            seller_name = product_info.get('seller_name', None)
            product_list.append({
                'product_id': str(_id),
                'product_title': product_name,
                'thumbnail': thumbnail,
                'seller_id': str(seller_id),
                'seller_name': seller_name
            })
    return product_list


def hashtag_detect(text):
    """
    Detect hashtags in a text.

    Args:
        text (str): The text to detect hashtags in

    Returns:
        list: A list of hashtags
    """
    if not text:
        return []

    hashtags = re.findall(r'#(\w+)', text)
    return hashtags

def convert_to_number(string):
    if string is None:
        return string
    string = string.lower()
    if isinstance(string, str):
        if 'k' in string:
            return int(float(string.replace('k', '')) * 1_000)
        elif 'm' in string:
            return int(float(string.replace('m', '')) * 1_000_000)
    return int(string)

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
