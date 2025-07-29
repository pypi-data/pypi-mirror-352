import pytest
from standard_open_inflation_package import BaseAPI, Handler, Response, NetworkError, Request, HandlerSearchFailedError, HttpMethod, Page
from io import BytesIO
from asyncio.exceptions import TimeoutError


CHECK_HTML = "https://httpbin.org"
TIMEOUT = 30.0


@pytest.mark.asyncio
async def test_interceptor_json():
    api = BaseAPI(timeout=TIMEOUT)
    await api.new_session()
    
    result = await api.new_direct_fetch(CHECK_HTML, handler=Handler.JSON())
    assert isinstance(result, Response), "Result should be an instance of Response"
    assert result.status == 200, f"Expected status 200, got {result.status}"
    assert isinstance(result.response, dict), "Response should be a dictionary"

    await api.close()

@pytest.mark.asyncio
async def test_interceptor_js():
    api = BaseAPI(timeout=TIMEOUT)
    await api.new_session()

    result = await api.new_direct_fetch(CHECK_HTML, handler=Handler.JS())
    assert isinstance(result, Response), "Result should be an instance of Response"
    assert result.status == 200, f"Expected status 200, got {result.status}"
    assert isinstance(result.response, str), "Response should be a string"

    await api.close()

@pytest.mark.asyncio
async def test_interceptor_css():
    api = BaseAPI(timeout=TIMEOUT)
    await api.new_session()

    result = await api.new_direct_fetch(CHECK_HTML, handler=Handler.CSS())
    assert isinstance(result, Response), "Result should be an instance of Response"
    assert result.status == 200, f"Expected status 200, got {result.status}"
    assert isinstance(result.response, str), "Response should be a string"

    await api.close()

@pytest.mark.asyncio
async def test_interceptor_image():
    api = BaseAPI(timeout=TIMEOUT)
    await api.new_session()

    result = await api.new_direct_fetch(CHECK_HTML, handler=Handler.IMAGE())
    assert isinstance(result, Response), "Result should be an instance of Response"
    assert result.status == 200, f"Expected status 200, got {result.status}"
    assert isinstance(result.response, BytesIO), "Response should be a BytesIO"

    await api.close()

@pytest.mark.asyncio
async def test_interceptor_video():
    api = BaseAPI(timeout=TIMEOUT)
    await api.new_session()

@pytest.mark.asyncio
async def test_interceptor_font():
    api = BaseAPI(timeout=TIMEOUT)
    await api.new_session()

@pytest.mark.asyncio
async def test_interceptor_application():
    api = BaseAPI(timeout=TIMEOUT)
    await api.new_session()

@pytest.mark.asyncio
async def test_interceptor_archive():
    api = BaseAPI(timeout=TIMEOUT)
    await api.new_session()

@pytest.mark.asyncio
async def test_interceptor_text():
    api = BaseAPI(timeout=TIMEOUT)
    await api.new_session()

@pytest.mark.asyncio
async def test_interceptor_any():
    api = BaseAPI(timeout=TIMEOUT)
    await api.new_session()

    result = await api.new_direct_fetch(CHECK_HTML, handler=Handler.ANY())
                
    assert isinstance(result, Response), "Result should be an instance of Response"
    assert result.status == 200, f"Expected status 200, got {result.status}"
    assert isinstance(result.response, (dict, str, BytesIO)), "Response should be a dict, str or BytesIO"

    await api.close()

@pytest.mark.asyncio
async def test_interceptor_nonexistent_url():
    api = BaseAPI(timeout=TIMEOUT)
    await api.new_session()

    result = await api.new_direct_fetch(CHECK_HTML, handler=Handler.IMAGE(startswith_url=f"{CHECK_HTML}/not/exist"))

    assert isinstance(result, HandlerSearchFailedError), "Result should be an instance of HandlerSearchFailedError"
    assert len(result.rejected_responses) > 0, "There should be rejected responses"
    assert abs(result.duration-TIMEOUT) < 0.2, "Duration should match the timeout"
    
    api._logger.debug("Rejected responses:")
    for i, response in enumerate(result.rejected_responses):
        api._logger.debug(f"{i+1}. {response}")

    await api.close()
