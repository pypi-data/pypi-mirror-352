from httpx import Response
from .exceptions import ShabtiRequestError
from shabti_types import CollectionExistsError


def raise_error(response: Response):
    body = response.json()
    if response.status_code == 500:
        if "error_type" in body:
            if body["error_type"] == "CollectionExistsError":
                raise CollectionExistsError

    raise ShabtiRequestError(status_code=response.status_code, message=body)
