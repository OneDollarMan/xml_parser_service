from unittest.mock import AsyncMock, patch, Mock
import anthropic
import pytest
from src.utils import get_claude_result


@pytest.mark.asyncio
async def test_get_claude_result_success():
    prompt = "Test prompt"
    expected_result = "Here is the analysis."

    mock_client = AsyncMock()
    mock_client.messages.create.return_value = Mock(content=[Mock(text=expected_result)])

    with patch("src.utils.client", mock_client):
        result = await get_claude_result(prompt)

        assert result == expected_result
        mock_client.messages.create.assert_called_once_with(
            model="claude-3-haiku-20240307",
            max_tokens=1000,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": prompt
                        }
                    ]
                }
            ]
        )


@pytest.mark.asyncio
async def test_get_claude_result_failure():
    prompt = "Test prompt"
    mock_client = AsyncMock()
    mock_client.messages.create.side_effect = anthropic.AnthropicError("API error")

    with patch("src.utils.client", mock_client):
        result = await get_claude_result(prompt)

        assert result is None
        mock_client.messages.create.assert_called_once()
