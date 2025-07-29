from http import HTTPStatus
from typing import Callable

import pytest
from faker import Faker
from starlette.exceptions import HTTPException

from fastapi_exception_responses.core import Responses

from utils import assert_value_type, assert_response_structure, get_responses


def test_single_response(responses_args: Callable):
    arg_name, code, detail = responses_args()
    responses = get_responses({arg_name: (code, detail)})

    assert_response_structure(responses, code, arg_name, detail)


def test_code_as_string(responses_args: Callable):
    arg_name, _, detail = responses_args()
    responses = get_responses({arg_name: ("404", detail)})
    print(responses)
    assert responses[404]


def test_multiple_responses(responses_args: Callable):
    argname1, code1, detail1 = responses_args()
    argname2, code2, detail2 = responses_args()

    responses = get_responses(
        {
            argname1: (code1, detail1),
            argname2: (code2, detail2),
        }
    )

    assert_response_structure(responses, code1, argname1, detail1)
    assert_response_structure(responses, code2, argname2, detail2)


def test_multiple_detail(responses_args: Callable):
    argname1, code1, detail1 = responses_args()
    argname2, _, detail2 = responses_args()

    responses = get_responses(
        {
            argname1: (code1, detail1),
            argname2: (code1, detail2),
        }
    )

    assert_response_structure(responses, code1, argname1, detail1)
    assert_response_structure(responses, str(code1), argname2, detail2)


def test_attr_is_replaced_with_http_exception(responses_args: Callable):
    argname, code, detail = responses_args()

    class R(Responses):
        VALUE = code, detail

    R.get_responses()

    assert isinstance(R.VALUE, HTTPException)
    assert R.VALUE.status_code == int(code)
    assert R.VALUE.detail == detail


def test_multiple_inheritance(responses_args: Callable):
    argname, code, detail = responses_args()
    child_argname, child_code, child_detail = responses_args()

    ParentResponse = type("SimpleResponse", (Responses,), {argname: (code, detail)})
    ChildResponses = type(
        "SimpleResponse", (ParentResponse,), {child_argname: (child_code, child_detail)}
    )

    responses = ChildResponses.get_responses()

    assert_response_structure(responses, code, argname, detail)
    assert_response_structure(responses, child_code, child_argname, child_detail)


def test_invalid_attr_name(responses_args: Callable):
    argname, code, detail = responses_args()

    argname1 = f"__{argname}__"
    argname2 = f"_{argname}"
    argname3 = f"__{argname}"

    responses = get_responses(
        {
            argname1: (code, detail),
            argname2: (code, detail),
            argname3: (code, detail),
        }
    )

    assert responses == {}


def test_callable_attr(responses_args: Callable):
    argname, code, _ = responses_args()

    def mock_func():
        pass

    responses_class = type("ResponsesClass", (Responses,), {argname: mock_func})

    assert responses_class.get_responses() == {}


def test_invalid_code_type(faker: Faker):
    assert_value_type(faker.pystr())
    assert_value_type(faker.pyint())
    assert_value_type(faker.pybool())
    assert_value_type(faker.pydict())
    assert_value_type(faker.pyset())
    assert_value_type(faker.pyfloat())
    assert_value_type(faker.pyobject())
    assert_value_type(faker.pylist(nb_elements=2))


def test_valid_description(faker: Faker, responses_args: Callable):
    argname, code, detail = responses_args()
    responses = get_responses({argname: (code, detail)})

    assert responses[code]["description"] == HTTPStatus(code).phrase


def test_invalid_tuple_len(responses_args: Callable, faker: Faker):
    argname, code, detail = responses_args()

    with pytest.raises(TypeError):
        get_responses({argname: (code, detail, faker.pystr())})

    with pytest.raises(TypeError):
        get_responses({argname: (code,)})
