from unittest.mock import patch
import pytest
from httpx import AsyncClient, ASGITransport
from src.main import app
from src.models import AnalyzeRequest


@pytest.mark.asyncio
async def test_post_upload_report_by_url():
    url = "http://example.com/report.xml"
    analyze_request = AnalyzeRequest(id=1, status=AnalyzeRequest.STATUS_CREATED, report_url=url)
    with patch("src.main.analyze_report.delay") as mock_analyze_report:
        with patch("src.main.create_analyze_request", return_value=analyze_request) as mock_create_request:
            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://testserver") as client:
                payload = {"url": url}

                response = await client.post("/upload_report_url/", json=payload)

                assert response.status_code == 200

                data = response.json()
                assert data["id"] == analyze_request.id
                assert data["report_url"] == analyze_request.report_url

                mock_create_request.assert_called_once()
                mock_analyze_report.assert_called_once_with(data["id"])
