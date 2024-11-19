import sys
from pathlib import Path
import pytest_asyncio
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from src.config import DATABASE_TEST_URL, PG_TEST_DB
from src.models import Base, AnalyzeRequest, Product

sys.path.append(str(Path(__file__).resolve().parent.parent / "src"))


@pytest_asyncio.fixture(scope="session", loop_scope="session", autouse=True)
async def init_db():
    postgres_engine = create_async_engine(DATABASE_TEST_URL, isolation_level="AUTOCOMMIT")
    test_engine = create_async_engine(DATABASE_TEST_URL + PG_TEST_DB)
    async with postgres_engine.connect() as conn:
        await conn.execute(text(f"DROP DATABASE IF EXISTS {PG_TEST_DB}"))

    async with postgres_engine.connect() as conn:
        await conn.execute(text(f"CREATE DATABASE {PG_TEST_DB}"))

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def async_session_maker():
    test_engine = create_async_engine(DATABASE_TEST_URL + PG_TEST_DB)
    yield async_sessionmaker(test_engine, expire_on_commit=False, class_=AsyncSession)


@pytest_asyncio.fixture
async def session(async_session_maker):
    async with async_session_maker() as session:
        yield session


@pytest_asyncio.fixture(autouse=True)
async def clear_database(session: AsyncSession):
    meta = Base.metadata
    async with session.begin():
        for table in reversed(meta.sorted_tables):
            await session.execute(text(f"DELETE FROM {table.name}"))
    await session.commit()


@pytest_asyncio.fixture
async def setup_test_request(session: AsyncSession):
    request = AnalyzeRequest(id=1, report_url="http://example.com/report")
    session.add(request)
    await session.commit()


@pytest_asyncio.fixture
async def setup_test_products(setup_test_request, session: AsyncSession):
    products = [
        Product(id=1, name="product1", request_id=1, category="Category1", price=10.0, quantity=5),
        Product(id=2, name="product2", request_id=1, category="Category2", price=15.0, quantity=10),
        Product(id=3, name="product3", request_id=1, category="Category1", price=20.0, quantity=3),
        Product(id=4, name="product4", request_id=1, category="Category3", price=5.0, quantity=8),
    ]
    session.add_all(products)
    await session.commit()