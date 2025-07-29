from typing import Any

from starlette.exceptions import HTTPException
from http import HTTPStatus


class Responses:
    __original_attrs = {}

    @classmethod
    def get_responses(cls) -> dict[int | str, dict[str, Any]]:
        """
        Generates documentation for OpenAPI and Endpoints starlette HTTPExceptions based on class attributes
        defined as tuples of status code and detail

        :return: A valid dictionary for the FastAPI decorator param 'responses'
        """

        responses_dict = {}
        for attr in dir(cls):
            if (
                not attr.startswith("__")
                and not callable(getattr(cls, attr))
                and not attr.startswith("_")
            ):
                value = getattr(cls, attr)

                if isinstance(value, tuple) and len(value) == 2:
                    status_code, detail = value

                    try:
                        HTTPStatus(int(status_code))
                    except ValueError as e:
                        raise e

                    if not (
                        isinstance(status_code, int)
                        or (isinstance(status_code, str) and status_code.isdigit())
                    ) or isinstance(status_code, bool):
                        raise TypeError(
                            f"Invalid status_code type: {type(status_code)}"
                        )

                    if not isinstance(detail, str):
                        raise TypeError(f"Invalid detail type: {type(detail)}")

                    if isinstance(status_code, str):
                        status_code = int(status_code)

                    cls.__original_attrs[attr] = status_code, detail
                elif attr in cls.__original_attrs:
                    status_code, detail = cls.__original_attrs[attr]

                else:
                    raise TypeError(
                        f"Attribute {attr} must be a (status_code, detail) tuple. Got: {value}"
                    )

                if status_code not in responses_dict.keys():
                    responses_dict[status_code] = {
                        "description": f"{HTTPStatus(status_code).phrase}",
                        "content": {"application/json": {"examples": {}}},
                    }

                responses_dict[status_code]["content"]["application/json"]["examples"][
                    attr.lower()
                ] = {
                    "summary": attr.replace("_", " "),
                    "value": {"detail": detail},
                }

                setattr(
                    cls,
                    attr,
                    HTTPException(status_code=int(status_code), detail=detail),
                )
        return responses_dict
