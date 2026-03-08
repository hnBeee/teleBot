import re

def is_valid_url(text: str) -> bool:
    """Mengecek apakah string berupa URL yang valid."""
    url_pattern = re.compile(
        r'^(https?:\/\/)?'  # http:// atau https://
        r'([\w\d\-]+\.)+\w{2,}(\/.*)?$' # domain dan path
    )
    return bool(url_pattern.match(text))