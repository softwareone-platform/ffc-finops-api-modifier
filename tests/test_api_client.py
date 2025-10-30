from unittest.mock import AsyncMock, patch

import pytest
from httpx import Headers, HTTPStatusError, RequestError, Response

from app.core.api_client import APIClient


@patch("httpx.AsyncClient.request")
async def test_make_request_success(mock_request, api_client, async_client):
    """Test a successful JSON response."""
    mock_response = Response(
        status_code=200,
        request=async_client.request,
        headers=Headers({"Content-Type": "application/json"}),
        json={"key": "value"},
    )
    mock_request.return_value = mock_response
    response = await api_client._make_request("GET", "/endpoint")
    assert response["status_code"] == 200
    assert response["data"] == {"key": "value"}
    assert "error" not in response


@patch("httpx.AsyncClient.request")
async def test_make_request_204_success(mock_request, api_client, async_client):
    """Test a successful JSON response."""
    mock_response = Response(status_code=204, request=async_client.request)
    mock_request.return_value = mock_response
    response = await api_client._make_request("GET", "/endpoint")
    assert response == {}


@patch("httpx.AsyncClient.request")
async def test_make_request_plain_text_response(mock_request, api_client, async_client):
    """Test handling of non-JSON responses."""
    mock_response = Response(
        status_code=200,
        request=async_client.request,
        headers=Headers({"Content-Type": "text/plain"}),
    )

    mock_request.return_value = mock_response
    response = await api_client._make_request("GET", "/endpoint")
    assert response["status_code"] == 403
    assert response["error"] == "Response is not JSON"


@patch("httpx.AsyncClient.request")
async def test_make_request_json_value_error_response(
    mock_request, api_client, async_client
):
    """Test handling of non-JSON responses."""
    mock_response = Response(
        status_code=200,
        request=async_client.request,
        headers=Headers({"Content-Type": "application/json"}),
    )

    def raise_value_error():
        raise ValueError("Invalid JSON")

    mock_response.json = raise_value_error
    mock_request.return_value = mock_response

    response = await api_client._make_request("GET", "/endpoint")

    assert response["status_code"] == 403
    assert response["error"] == "Invalid JSON format in response"


@patch("httpx.AsyncClient.request")
async def test_make_request_http_request_error(mock_request, api_client, async_client):
    mock_request.side_effect = RequestError(
        "Connection failed", request=async_client.request
    )
    response = await api_client._make_request("GET", "/endpoint")

    assert response["status_code"] == 503
    assert response["data"] == {}
    assert response["error"] == "Connection error: Connection failed"


@patch("httpx.AsyncClient.request")
async def test_make_request_http_status_error(mock_request, api_client, async_client):
    # Create a mock Response object
    mock_response = Response(
        status_code=404,
        request=async_client.request,
        headers={"Content-Type": "application/json"},
        json={"detail": "Not Found"},
    )
    # Simulate raising an HTTPStatusError
    mock_request.side_effect = HTTPStatusError(
        message="HTTP error",
        request=async_client.request,
        response=mock_response,
    )

    response = await api_client._make_request("GET", "/endpoint")

    assert response["status_code"] == 404
    assert response["data"] == {"detail": "Not Found"}
    assert response["error"] == 'HTTP error: 404 - {"detail":"Not Found"}'


@patch("httpx.AsyncClient.request")
async def test_make_request_generic_exception_logging(async_client, caplog, api_client):
    """Test logging of generic exceptions."""
    # Simulate raising a generic Exception
    async_client.side_effect = Exception("Something went wrong")

    # Perform the request with logging enabled
    with caplog.at_level("ERROR"):
        response = await api_client._make_request("GET", "/endpoint")
        assert response["status_code"] == 500
        assert response["data"] == {}
        assert response["error"] == "Unexpected error: Something went wrong"

    # Assertions for logging
    assert any(
        "An unexpected error occurred: Something went wrong" in record.message
        for record in caplog.records
    )


@pytest.mark.parametrize(
    "method, endpoint, status_code, expected_data",  # noqa: PT006
    [
        ("GET", "/endpoint", 200, {"key": "value"}),
        ("POST", "/endpoint", 201, {"key": "value"}),
        ("PUT", "/endpoint", 200, {"key": "value"}),
        ("PATCH", "/endpoint", 200, {"key": "value"}),
        ("DELETE", "/endpoint", 204, None),
    ],
)
async def test_api_client_methods(
    api_client, method, endpoint, status_code, expected_data
):
    """Test APIClient HTTP methods."""
    api_client._make_request = AsyncMock(
        return_value={"status_code": status_code, "data": expected_data}
    )

    # Map the method to the corresponding APIClient function
    method_function_map = {
        "GET": api_client.get,
        "POST": api_client.post,
        "PUT": api_client.put,
        "PATCH": api_client.patch,
        "DELETE": api_client.delete,
    }

    if method in ["GET", "DELETE"]:
        response = await method_function_map[method](
            endpoint,
            headers={"Authorization": "Bearer token"},
            params={"query": "who are you"},
        )
        api_client._make_request.assert_called_once_with(
            method,
            endpoint,
            params={"query": "who are you"},
            headers={"Authorization": "Bearer token"},
        )
    else:
        response = await method_function_map[method](
            endpoint, headers={"Authorization": "Bearer token"}, data={"key": "value"}
        )
        api_client._make_request.assert_called_once_with(
            method,
            endpoint,
            headers={"Authorization": "Bearer token"},
            data={"key": "value"},
        )

    assert response["status_code"] == status_code
    assert response["data"] == expected_data


async def test_api_client_close():
    """Test the close method of APIClient."""
    # Create an APIClient instance
    client = APIClient(base_url="http://testserver")

    # Mock the aclose method of the AsyncClient
    client.client.aclose = AsyncMock()

    # Call the close method
    await client.close()

    # Assert that aclose was called
    client.client.aclose.assert_called_once()
