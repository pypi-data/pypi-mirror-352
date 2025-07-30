from typing import Optional
from uuid import uuid4
import string
import random


HTTP_HEADER_CORRELATION_ID = "X-Correlation-ID"
HTTP_HEADER_TRACE_ID = "X-Trace-ID"
HTTP_HEADER_SPAN_ID = "X-Span-ID"
HTTP_AUTHORIZATION_HEADER = "Authorization"

ASYNC_CONTEXT_CORRELATION_ID = "correlation_id"
ASYNC_CONTEXT_TRACE_ID = "trace_id"
ASYNC_CONTEXT_SPAN_ID = "span_id"
ASYNC_CONTEXT_TOPIC = "topic"
ASYNC_CONTEXT_SUBTOPIC = "subtopic"
ASYNC_CONTEXT_AUTHORIZATION = "auth"


def id_generator(size=5, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


def default_correlation_id(
    service_name: Optional[str] = "DEFAULT",
) -> str:
    return f"{service_name}-{id_generator()}"


def default_span_id() -> str:
    return str(uuid4())


def default_trace_id() -> str:
    return str(uuid4())


def add_hop_to_correlation(
    correlation_id: str,
) -> str:
    hop = id_generator()
    return f"{correlation_id}-{hop}"
