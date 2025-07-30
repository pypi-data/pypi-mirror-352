import base64
import hashlib
import random
import string
from urllib.parse import urlparse


def random_string():
    return ''.join(random.choice(string.ascii_letters) for _ in range(50))


def hash_it(text: str):
    text = hashlib.sha256(text.encode()).digest()
    text = base64.urlsafe_b64encode(text).decode()
    return text.replace("=", "")


def parse_response_url(token: str) -> dict:
    """Parses a response token."""
    print(">> Parsing response token.")
    try:
        url = urlparse(token)
        print('url=', url)
        params = url.fragment.split('&')
        print('params=', params)
        response = {}
        for param in params:
            print('param=', param)
            response = {
                **response,
                param.split('=')[0]: param.split('=')[1]
            }
        print('response=', response)
        return response
    except Exception as exc:
        raise ValueError("Invalid token provided.") from exc

