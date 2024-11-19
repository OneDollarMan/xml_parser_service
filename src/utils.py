import asyncio
import logging
from datetime import datetime
import aiohttp
import xml.etree.ElementTree as ET
import anthropic
from config import ANTHROPIC_API_KEY

client = anthropic.AsyncAnthropic(api_key=ANTHROPIC_API_KEY)
logger = logging.getLogger('celery')


async def download_report(url: str):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=10) as resp:
                text = await resp.text()
                if resp.status != 200:
                    logger.warning(f'Request failed, {resp.status=}, {text=}')
                    return None
                return text
    except aiohttp.ClientError as e:
        logger.error(f"Network error while fetching {url}: {e}")
    except asyncio.TimeoutError:
        logger.error(f"Request to {url} timed out.")
    except UnicodeDecodeError as e:
        logger.error(f"Failed to decode response from {url}: {e}")
    except Exception as e:
        logger.error(f"Unexpected error while downloading report from {url}: {e}")
    return None


def parse_sales_report_xml(report_str: str) -> (datetime | None, list[dict]):
    try:
        root = ET.fromstring(report_str)
        if root.tag != "sales_data":
            logger.error("Invalid root element: expected 'sales_data'")
            return None, []
    except (ET.ParseError, TypeError) as e:
        logger.error(f"Error parsing report: {e}")
        return None, []

    try:
        report_date = datetime.strptime(root.attrib.get("date"), '%Y-%m-%d')
    except (TypeError, ValueError) as e:
        logger.error(f"Invalid or missing report date in XML: {e}")
        return None, []

    products = []
    for product_elem in root.findall("./products/product"):
        try:
            product = {
                "name": product_elem.find("name").text,
                "quantity": int(product_elem.find("quantity").text),
                "price": float(product_elem.find("price").text),
                "category": product_elem.find("category").text,
            }
        except (AttributeError, ValueError) as e:
            logger.error(f"Error parsing product, skipping: {e}")
            continue
        products.append(product)

    logger.info(f"Parsed {report_date=} report and {len(products)} products")
    return report_date, products


def create_prompt(report_date: datetime, total_revenue: float, top_products: str, categories: str) -> str:
    return (
        f'Проанализируй данные о продажах за {report_date.date()}:\n '
        f'1. Общая выручка: {total_revenue}\n'
        f'2. Топ-3 товара по продажам: {top_products}\n'
        f'3. Распределение по категориям: {categories}\n'
        f'Составь краткий аналитический отчет с выводами и рекомендациями.'
    )


async def get_claude_result(prompt: str) -> str | None:
    try:
        message = await client.messages.create(
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
        if len(message.content) > 0:
            return message.content[0].text
        else:
            logger.error('Claude returned nothing(')
    except anthropic.AnthropicError as e:
        logger.error(f"Error getting claude result: {e}")
        return None
