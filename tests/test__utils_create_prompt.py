from datetime import datetime
from src.utils import create_prompt


def test_create_prompt():
    report_date = datetime(2024, 1, 1)
    total_revenue = 1000.0
    top_products = "Product1, Product2, Product3"
    categories = "Category1: 50%, Category2: 30%, Category3: 20%"

    prompt = create_prompt(report_date, total_revenue, top_products, categories)

    expected_prompt = (
        "Проанализируй данные о продажах за 2024-01-01:\n "
        "1. Общая выручка: 1000.0\n"
        "2. Топ-3 товара по продажам: Product1, Product2, Product3\n"
        "3. Распределение по категориям: Category1: 50%, Category2: 30%, Category3: 20%\n"
        "Составь краткий аналитический отчет с выводами и рекомендациями."
    )
    assert prompt == expected_prompt
