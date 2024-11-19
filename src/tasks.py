import logging
from celery import Celery
import asyncio
from celery.signals import setup_logging
from db import async_session_maker
from models import Product, AnalyzeRequest
from service import get_top3_products, get_total_revenue, get_categories_distribution, get_request_by_id
from utils import download_report, parse_sales_report_xml, create_prompt, get_claude_result
from config import RABBITMQ_URL, config_logging

app = Celery('celery', broker=RABBITMQ_URL)

@setup_logging.connect
def config_loggers(*args, **kwags):
    config_logging()

logger = logging.getLogger('celery')


async def analyze_report_async(request_id: int):
    async with async_session_maker() as session:
        request = await get_request_by_id(session, request_id)
        if not request:
            logger.warning(f'No analyze request found for {request_id=}')
            return

        report_str = await download_report(request.report_url)
        if not report_str:
            logger.warning(f'Error downloading xml report for {request_id=}')
            request.status = AnalyzeRequest.STATUS_ERROR
            await session.commit()
            return

        report_date, report_products = parse_sales_report_xml(report_str)
        if not report_date:
            logger.warning(f'Error parsing xml report for {request_id=}')
            request.status = AnalyzeRequest.STATUS_ERROR
            await session.commit()
            return

        request.report_date = report_date
        for product in report_products:
            session.add(
                Product(
                    request_id=request.id,
                    name=product['name'],
                    quantity=product['quantity'],
                    price=product['price'],
                    category=product['category'],
                )
            )

        total_revenue = await get_total_revenue(session, request_id)
        top_products = await get_top3_products(session, request_id)
        top_products = ', '.join([str(product.name) for product in top_products])
        categories = await get_categories_distribution(session, request_id)
        categories = ', '.join([f'{category}: {quantity} pcs' for category, quantity in categories])

        prompt = create_prompt(
            report_date=request.report_date,
            total_revenue=total_revenue,
            top_products=top_products,
            categories=categories
        )
        llm_result = await get_claude_result(prompt)
        if not llm_result:
            logger.warning(f'Error getting claude result for {request_id=}')
            request.status = AnalyzeRequest.STATUS_ERROR
            await session.commit()
            return

        request.llm_result = llm_result
        request.status = AnalyzeRequest.STATUS_FINISHED
        await session.commit()
        return request_id


@app.task
def analyze_report(args):
    loop = asyncio.get_event_loop()
    if loop.is_running():
        new_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(new_loop)
        res = new_loop.run_until_complete(analyze_report_async(args))
        new_loop.close()
        return res
    else:
        return loop.run_until_complete(analyze_report_async(args))
