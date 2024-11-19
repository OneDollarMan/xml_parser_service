from typing import Sequence
from sqlalchemy import select, func, Row
from sqlalchemy.ext.asyncio import AsyncSession
from models import AnalyzeRequest, Product
from schemas import UploadReportSchema


async def create_analyze_request(session: AsyncSession, schema: UploadReportSchema) -> AnalyzeRequest:
    request = AnalyzeRequest(report_url=schema.url.unicode_string())
    session.add(request)
    await session.commit()
    await session.refresh(request)
    return request


async def get_request_by_id(session: AsyncSession, request_id: int) -> AnalyzeRequest | None:
    request = await session.execute(
        select(AnalyzeRequest).filter(AnalyzeRequest.id == request_id)
    )
    return request.scalar()


async def get_total_revenue(session: AsyncSession, request_id: int) -> float:
    total_revenue = await session.execute(
        select(
            func.sum(Product.price * Product.quantity)
        ).filter(
            Product.request_id == request_id
        ).group_by(Product.request_id)
    )
    return total_revenue.scalar() or 0.0


async def get_top3_products(session: AsyncSession, request_id: int) -> Sequence[Product]:
    top_products = await session.execute(
        select(Product).filter(
            Product.request_id == request_id
        ).order_by(
            Product.quantity.desc()
        ).limit(3)
    )
    return top_products.scalars().all()


async def get_categories_distribution(session: AsyncSession, request_id: int) -> Sequence[Row[tuple[str, int]]]:
    categories = await session.execute(
        select(
            Product.category, func.sum(Product.quantity)
        ).filter(
            Product.request_id == request_id
        ).group_by(Product.category)
    )
    return categories.all()
