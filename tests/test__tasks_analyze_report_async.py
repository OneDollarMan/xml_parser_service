import pytest
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime

from sqlalchemy import select

from src.tasks import analyze_report_async
from src.models import AnalyzeRequest, Product


@pytest.mark.asyncio
async def test_analyze_report_success(async_session_maker, setup_test_request):
    report_date = datetime(2024, 1, 1)
    mock_request = Mock(
        id=1,
        report_url="http://example.com/report.xml",
        status=AnalyzeRequest.STATUS_CREATED
    )
    mock_products = [
        {"name": "Product1", "quantity": 10, "price": 100, "category": "A"},
        {"name": "Product2", "quantity": 5, "price": 200, "category": "B"}
    ]
    mock_top_products = [Mock(name="Product1"), Mock(name="Product2")]

    # Setup mocks
    with patch("src.tasks.async_session_maker", async_session_maker), \
            patch("src.tasks.get_request_by_id", AsyncMock(return_value=mock_request)), \
            patch("src.tasks.download_report", AsyncMock(return_value="<xml>report</xml>")), \
            patch("src.tasks.parse_sales_report_xml", return_value=(report_date, mock_products)), \
            patch("src.tasks.get_total_revenue", AsyncMock(return_value=1500)), \
            patch("src.tasks.get_top3_products", AsyncMock(return_value=mock_top_products)), \
            patch("src.tasks.get_categories_distribution",
                  AsyncMock(return_value=[("A", 10), ("B", 5)])), \
            patch("src.tasks.get_claude_result", AsyncMock(return_value="Analysis complete")):
        result = await analyze_report_async(mock_request.id)

        # Assertions
        assert result == mock_request.id
        assert mock_request.status == AnalyzeRequest.STATUS_FINISHED
        assert mock_request.report_date == report_date
        assert mock_request.llm_result == "Analysis complete"


@pytest.mark.asyncio
async def test_analyze_report_no_request(async_session_maker):
    with patch("src.tasks.async_session_maker", async_session_maker), \
            patch("src.tasks.get_request_by_id", AsyncMock(return_value=None)):
        result = await analyze_report_async(1)
        assert result is None


@pytest.mark.asyncio
async def test_analyze_report_download_error(async_session_maker):
    mock_request = Mock(id=1, report_url="http://example.com/report.xml")

    with patch("src.tasks.async_session_maker", async_session_maker), \
            patch("src.tasks.get_request_by_id", AsyncMock(return_value=mock_request)), \
            patch("src.tasks.download_report", AsyncMock(return_value=None)):
        await analyze_report_async(1)
        assert mock_request.status == AnalyzeRequest.STATUS_ERROR


@pytest.mark.asyncio
async def test_analyze_report_parse_error(async_session_maker):
    mock_request = Mock(id=1, report_url="http://example.com/report.xml")

    with patch("src.tasks.async_session_maker", async_session_maker), \
            patch("src.tasks.get_request_by_id", AsyncMock(return_value=mock_request)), \
            patch("src.tasks.download_report", AsyncMock(return_value="<xml>report</xml>")), \
            patch("src.tasks.parse_sales_report_xml", return_value=(None, None)):
        await analyze_report_async(1)
        assert mock_request.status == AnalyzeRequest.STATUS_ERROR


@pytest.mark.asyncio
async def test_analyze_report_claude_error(setup_test_request, async_session_maker):
    mock_request = Mock(id=1, report_url="http://example.com/report.xml")

    mock_products = [
        {"name": "Product1", "quantity": 10, "price": 100, "category": "A"}
    ]

    with patch("src.tasks.async_session_maker", async_session_maker), \
            patch("src.tasks.get_request_by_id", AsyncMock(return_value=mock_request)), \
            patch("src.tasks.download_report", AsyncMock(return_value="<xml>report</xml>")), \
            patch("src.tasks.parse_sales_report_xml",
                  return_value=(datetime(2024, 1, 1), mock_products)), \
            patch("src.tasks.get_total_revenue", AsyncMock(return_value=1000)), \
            patch("src.tasks.get_top3_products",
                  AsyncMock(return_value=[Mock(name="Product1")])), \
            patch("src.tasks.get_categories_distribution",
                  AsyncMock(return_value=[("A", 10)])), \
            patch("src.tasks.get_claude_result", AsyncMock(return_value=None)):
        await analyze_report_async(1)

        assert mock_request.status == AnalyzeRequest.STATUS_ERROR


@pytest.mark.asyncio
async def test_product_creation(setup_test_request, async_session_maker):
    mock_request = Mock(id=1, report_url="http://example.com/report.xml")

    mock_products = [
        {"name": "Product1", "quantity": 10, "price": 100, "category": "A"},
        {"name": "Product2", "quantity": 5, "price": 200, "category": "B"}
    ]

    with patch("src.tasks.async_session_maker", async_session_maker), \
            patch("src.tasks.get_request_by_id", AsyncMock(return_value=mock_request)), \
            patch("src.tasks.download_report", AsyncMock(return_value="<xml>report</xml>")), \
            patch("src.tasks.parse_sales_report_xml",
                  return_value=(datetime(2024, 1, 1), mock_products)), \
            patch("src.tasks.get_total_revenue", AsyncMock(return_value=1000)), \
            patch("src.tasks.get_top3_products",
                  AsyncMock(return_value=[Mock(name="Product1")])), \
            patch("src.tasks.get_categories_distribution",
                  AsyncMock(return_value=[("A", 10)])), \
            patch("src.tasks.get_claude_result", AsyncMock(return_value="Analysis")):
        await analyze_report_async(1)

    async with async_session_maker() as async_session:
        products = await async_session.execute(select(Product))
        products = products.scalars().all()
        assert len(products) == len(mock_products)