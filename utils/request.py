from requests import Response
from ..exceptions import RequestException


def validate_response(response: Response, status_code: int, msg: str = None) -> Response:
    if response.status_code != status_code:
        err = f"request failed with status code {response.status_code}" + (f": {msg}" if msg else "")
        print(response.text)

        raise RequestException(err)

    return response
