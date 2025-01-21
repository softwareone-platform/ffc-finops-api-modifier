from app.core.exceptions import APIResponseError, AuthException


async def test_api_response_exception_empty_params():
    status_code = 403
    reason = "Wrong Operation"
    error_code = "ABC_123"
    title = "Authentication Error"
    params = ["Invalid arg"]
    exception = APIResponseError(
        status_code=status_code,
        reason=reason,
        error_code=error_code,
        title=title,
        params=params,
    )
    assert exception.status_code == status_code
    assert exception.title == title
    assert exception.error["status_code"] == status_code
    assert exception.error["reason"] == reason
    assert exception.error["error_code"] == error_code
    assert exception.error["params"] == params

    # Test with default params
    exception_no_params = APIResponseError(
        status_code=status_code,
        reason=reason,
        error_code=error_code,
        title=title,
    )
    assert exception_no_params.error["params"] == []


async def test_auth_exception_empty_params():
    status_code = 401
    reason = "Unauthorized"
    error_code = "AUTH_001"
    title = "Authentication Error"
    params = ["Invalid token"]
    exception = AuthException(
        status_code=status_code,
        reason=reason,
        error_code=error_code,
        title=title,
        params=params,
    )
    assert exception.status_code == status_code
    assert exception.title == title
    assert exception.error["status_code"] == status_code
    assert exception.error["reason"] == reason
    assert exception.error["error_code"] == error_code
    assert exception.error["params"] == params

    # Test with default params
    exception_no_params = AuthException(
        status_code=status_code,
        reason=reason,
        error_code=error_code,
        title=title,
    )
    assert exception_no_params.error["params"] == []
