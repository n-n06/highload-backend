from hashlib import sha256
from typing import Any
import json


def make_key(*args, **kwargs) -> str:
    parts = list(args)

    if kwargs:
        for key in sorted(kwargs.keys()):
            parts.append(f"{key}={kwargs[key]}")


    content = ":".join(str(p) for p in parts)

    key_hash = sha256(content.encode("utf-8")).hexdigest()[:16]

    return f"{content}:{key_hash}"
