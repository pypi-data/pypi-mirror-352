import functools

from pydantic import ValidationError

from common.parse import get_data_from_request
from common.responses import JsonStringResponse


def use_payload(payload_class):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(request, *args, **kwargs):
            data = get_data_from_request(request)

            try:
                payload = payload_class(**data)
            except ValidationError as e:
                return JsonStringResponse(e.json(), status=400)

            return func(request, *args, payload=payload, **kwargs)

        return wrapper

    return decorator
