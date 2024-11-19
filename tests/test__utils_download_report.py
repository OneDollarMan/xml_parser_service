from unittest.mock import patch, Mock
import pytest
from aiohttp import ClientError
from aiohttp.test_utils import make_mocked_coro
from src.utils import download_report


@pytest.mark.asyncio
async def test_successful_download():
    response = Mock()
    response.status = 200
    response.text = make_mocked_coro(return_value="report content")

    context_manager = Mock()
    context_manager.__aenter__ = make_mocked_coro(return_value=response)
    context_manager.__aexit__ = make_mocked_coro(return_value=None)

    session = Mock()
    session.get = Mock(return_value=context_manager)

    client_session = Mock()
    client_session.__aenter__ = make_mocked_coro(return_value=session)
    client_session.__aexit__ = make_mocked_coro(return_value=None)

    with patch('aiohttp.ClientSession', return_value=client_session):
        result = await download_report("http://example.com/report")

    assert result == "report content"


@pytest.mark.asyncio
async def test_failed_status_code():
    response = Mock()
    response.status = 404
    response.text = make_mocked_coro(return_value="not found")

    context_manager = Mock()
    context_manager.__aenter__ = make_mocked_coro(return_value=response)
    context_manager.__aexit__ = make_mocked_coro(return_value=None)

    session = Mock()
    session.get = Mock(return_value=context_manager)

    client_session = Mock()
    client_session.__aenter__ = make_mocked_coro(return_value=session)
    client_session.__aexit__ = make_mocked_coro(return_value=None)

    with patch('aiohttp.ClientSession', return_value=client_session):
        with patch('src.utils.logger') as mock_logger:
            result = await download_report("http://example.com/report")

    assert result is None
    mock_logger.warning.assert_called_once()
    assert "404" in mock_logger.warning.call_args[0][0]


@pytest.mark.asyncio
async def test_network_error():
    session = Mock()
    session.get = Mock(side_effect=ClientError("Network error occurred"))

    client_session = Mock()
    client_session.__aenter__ = make_mocked_coro(return_value=session)
    client_session.__aexit__ = make_mocked_coro(return_value=None)

    with patch('aiohttp.ClientSession', return_value=client_session):
        with patch('src.utils.logger') as mock_logger:
            result = await download_report("http://example.com/report")

    assert result is None
    mock_logger.error.assert_called_once()
    assert "Network error" in mock_logger.error.call_args[0][0]
