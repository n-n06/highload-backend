from hashlib import sha256
from typing import Any

def make_key(
    f: Any,
    instance: Any,
    content: str, *args
):
    
    key = "note:" + sha256(content.encode("utf-8")).hexdigest()
    # print("Generated key: ", key)
    return key
