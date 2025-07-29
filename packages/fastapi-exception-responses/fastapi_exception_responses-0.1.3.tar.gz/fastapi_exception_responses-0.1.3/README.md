# fastapi-responses

FastAPI Responses generates documentation for OpenAPI and Endpoints **starlette**
`HTTPExceptions` based on class attributes
defined as tuples of status code and detail

## Usage

### Configuration

```python
from fastapi import APIRouter

()
from fastapi_exception_responses import Responses

router = APIRouter()


class DemoResponses(Responses):
    NOT_VALID_EMAIL = 422, "Provided email is not valid."
    NOT_VALID_USERNAME = 422, "Provided username is already in use."
    WRONG_CREDENTIAL = 401, "Invalid username or password."


@router.get("/", responses=DemoResponses.get_responses())
async def get_demo():
    if condition_one:
        raise DemoResponses.NOT_VALID_USERNAME
    elif condition_two:
        raise DemoResponses.NOT_VALID_EMAIL
    else:
        raise DemoResponses.WRONG_CREDENTIAL
```

### Result

https://github.com/max31ru12/fastapi-responses/blob/main/img.png
