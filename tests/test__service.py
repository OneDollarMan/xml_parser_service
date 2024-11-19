import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from src.schemas import UploadReportSchema
from src.service import (
    create_analyze_request,
    get_request_by_id,
    get_total_revenue,
    get_top3_products,
    get_categories_distribution,
)

@pytest.mark.asyncio
async def test_create_analyze_request(session: AsyncSession):
    schema = UploadReportSchema(url="http://example.com/new-report")
    new_request = await create_analyze_request(session, schema)

    assert new_request.id is not None
    assert new_request.report_url == "http://example.com/new-report"


@pytest.mark.asyncio
async def test_get_request_by_id(session: AsyncSession, setup_test_products):
    fetched_request = await get_request_by_id(session, 1)

    assert fetched_request is not None
    assert fetched_request.id == 1
    assert fetched_request.report_url == "http://example.com/report"


@pytest.mark.asyncio
async def test_get_total_revenue(session: AsyncSession, setup_test_products):
    revenue = await get_total_revenue(session, 1)

    expected_revenue = (10.0 * 5) + (15.0 * 10) + (20.0 * 3) + (5.0 * 8)
    assert revenue == expected_revenue


@pytest.mark.asyncio
async def test_get_top3_products(session: AsyncSession, setup_test_products):
    top3_products = await get_top3_products(session, 1)

    assert len(top3_products) == 3
    assert top3_products[0].quantity == 10
    assert top3_products[1].quantity == 8
    assert top3_products[2].quantity == 5


@pytest.mark.asyncio
async def test_get_categories_distribution(session: AsyncSession, setup_test_products):
    categories_distribution = await get_categories_distribution(session, 1)

    expected_distribution = [
        ("Category1", 8),
        ("Category2", 10),
        ("Category3", 8),
    ]
    assert len(categories_distribution) == len(expected_distribution)
    for actual, expected in zip(categories_distribution, expected_distribution):
        assert actual[0] == expected[0]  # Category
        assert actual[1] == expected[1]  # Quantity
