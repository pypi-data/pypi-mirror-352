import pytest
from laserfocus.utils.response import Response

def test_response_init():
    response = Response("success", "test content")
    assert response.status == "success"
    assert response.content == "test content"

def test_response_success():
    response_dict = Response.success("test success")
    assert response_dict["status"] == "success"
    assert response_dict["content"] == "test success"

def test_response_error():
    response_dict = Response.error("test error")
    assert response_dict["status"] == "error"
    assert response_dict["content"] == "test error"

def test_response_to_dict():
    response = Response("custom", {"key": "value"})
    response_dict = response.to_dict()
    assert response_dict == {
        "status": "custom",
        "content": {"key": "value"}
    } 