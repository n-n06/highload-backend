import time

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from starlette.types import Message

from src import flatten_dict
from src import logger


class LogMiddleware(BaseHTTPMiddleware):
    """
    Middleware that logs structured json logs 
    """

    async def dispatch(self, request: Request, call_next):
        start_time = time.time()

        body_bytes = await request.body()
        body_text = body_bytes.decode("utf-8") if body_bytes else None

        async def receive() -> Message:
            return {"type": "http.request",
                    "body": body_bytes, 
                    "more_body": False}

        request = Request(request.scope, receive=receive)

        try:
            response: Response = await call_next(request)
            process_time = round((time.time() - start_time) * 1000, 2)
        except Exception as exc:
            logger.exception("Request failed")
            raise exc

        resp_body = b""
        async for chunk in response.body_iterator:
            resp_body += chunk
        response.body_iterator = iterate_in_memory(resp_body)

        try:
            resp_text = resp_body.decode("utf-8")
        except Exception:
            resp_text = "<non-text-response>"

        def sanitize_headers(headers: dict):
            SENSITIVE = {"authorization", "cookie"}
            return {k: v for k, v in headers.items() if k.lower() not in SENSITIVE}

        MAX_LEN = 2000
        if body_text and len(body_text) > MAX_LEN:
            body_text = body_text[:MAX_LEN] + "..."
        if resp_text and len(resp_text) > MAX_LEN:
            resp_text = resp_text[:MAX_LEN] + "..."

        log_data = {
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
            "method": request.method,
            "path": request.url.path,
            "query": str(request.url.query),
            "status_code": response.status_code,
            "process_time_ms": process_time,
            "client_ip": request.client.host if request.client else None,
        }

        nested_fields = { 
            "request": {
                "headers": sanitize_headers(dict(request.headers)),
                "body": body_text,
            },
            "response": {
                "headers": dict(response.headers),
                "body": resp_text,
            }
        }

        log_data.update(flatten_dict(nested_fields, sep="_"))
        
        logger.info("Request Log", extra=log_data)
        return response


async def iterate_in_memory(data: bytes):
    """Helper to replay response body from memory."""
    yield data

