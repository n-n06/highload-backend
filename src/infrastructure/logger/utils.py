from starlette.types import Message


def sanitize_headers(headers: dict):
    SENSITIVE = {"authorization", "cookie"}
    return {k: v for k, v in headers.items() if k.lower() not in SENSITIVE}


def flatten_dict(d, parent_key="", sep="_"):
    items = []

    for k,v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep).items())
        else:
            items.append((k, v))

    return dict(items)




async def iterate_in_memory(data: bytes):
    """Helper to replay response body from memory."""
    yield data
