from datetime import datetime
from unittest.mock import patch
from src.utils import parse_sales_report_xml


def test_successful_parse():
    xml_str = """
    <sales_data date="2024-03-15">
        <products>
            <product>
                <name>Laptop</name>
                <quantity>10</quantity>
                <price>999.99</price>
                <category>Electronics</category>
            </product>
            <product>
                <name>Mouse</name>
                <quantity>50</quantity>
                <price>29.99</price>
                <category>Accessories</category>
            </product>
        </products>
    </sales_data>
    """

    with patch('src.utils.logger') as mock_logger:
        report_date, products = parse_sales_report_xml(xml_str)

    assert report_date == datetime(2024, 3, 15)
    assert len(products) == 2

    assert products[0] == {
        "name": "Laptop",
        "quantity": 10,
        "price": 999.99,
        "category": "Electronics"
    }

    assert products[1] == {
        "name": "Mouse",
        "quantity": 50,
        "price": 29.99,
        "category": "Accessories"
    }

    mock_logger.info.assert_called_once()
    assert "Parsed" in mock_logger.info.call_args[0][0]
    assert "2 products" in mock_logger.info.call_args[0][0]


def test_invalid_root_element():
    xml_str = """
    <report date="2024-03-15">
        <products>
            <product>
                <name>Laptop</name>
                <quantity>10</quantity>
                <price>999.99</price>
                <category>Electronics</category>
            </product>
        </products>
    </report>
    """

    with patch('src.utils.logger') as mock_logger:
        report_date, products = parse_sales_report_xml(xml_str)

    assert report_date is None
    assert products == []
    mock_logger.error.assert_called_once()
    assert "Invalid root element" in mock_logger.error.call_args[0][0]


def test_invalid_xml():
    invalid_xml = "<sales_data date='2024-03-15'><invalid>"

    with patch('src.utils.logger') as mock_logger:
        report_date, products = parse_sales_report_xml(invalid_xml)

    assert report_date is None
    assert products == []
    mock_logger.error.assert_called_once()
    assert "Error parsing report" in mock_logger.error.call_args[0][0]


def test_none_input():
    with patch('src.utils.logger') as mock_logger:
        report_date, products = parse_sales_report_xml(None)

    assert report_date is None
    assert products == []
    mock_logger.error.assert_called_once()
    assert "Error parsing report" in mock_logger.error.call_args[0][0]


def test_invalid_date_format():
    xml_str = """
    <sales_data date="15-03-2024">
        <products>
            <product>
                <name>Laptop</name>
                <quantity>10</quantity>
                <price>999.99</price>
                <category>Electronics</category>
            </product>
        </products>
    </sales_data>
    """

    with patch('src.utils.logger') as mock_logger:
        report_date, products = parse_sales_report_xml(xml_str)

    assert report_date is None
    assert products == []
    mock_logger.error.assert_called_once()
    assert "Invalid or missing report date" in mock_logger.error.call_args[0][0]


def test_missing_date():
    xml_str = """
    <sales_data>
        <products>
            <product>
                <name>Laptop</name>
                <quantity>10</quantity>
                <price>999.99</price>
                <category>Electronics</category>
            </product>
        </products>
    </sales_data>
    """

    with patch('src.utils.logger') as mock_logger:
        report_date, products = parse_sales_report_xml(xml_str)

    assert report_date is None
    assert products == []
    mock_logger.error.assert_called_once()
    assert "Invalid or missing report date" in mock_logger.error.call_args[0][0]


def test_invalid_product_data():
    xml_str = """
    <sales_data date="2024-03-15">
        <products>
            <product>
                <name>Laptop</name>
                <quantity>invalid</quantity>
                <price>999.99</price>
                <category>Electronics</category>
            </product>
            <product>
                <name>Mouse</name>
                <quantity>50</quantity>
                <price>29.99</price>
                <category>Accessories</category>
            </product>
        </products>
    </sales_data>
    """

    with patch('src.utils.logger') as mock_logger:
        report_date, products = parse_sales_report_xml(xml_str)

    assert report_date == datetime(2024, 3, 15)
    assert len(products) == 1  # Only the valid product should be included
    assert products[0]["name"] == "Mouse"
    mock_logger.error.assert_called_once()
    assert "Error parsing product" in mock_logger.error.call_args[0][0]


def test_missing_product_fields():
    xml_str = """
    <sales_data date="2024-03-15">
        <products>
            <product>
                <name>Laptop</name>
                <price>999.99</price>
                <category>Electronics</category>
            </product>
            <product>
                <name>Mouse</name>
                <quantity>50</quantity>
                <price>29.99</price>
                <category>Accessories</category>
            </product>
        </products>
    </sales_data>
    """

    with patch('src.utils.logger') as mock_logger:
        report_date, products = parse_sales_report_xml(xml_str)

    assert report_date == datetime(2024, 3, 15)
    assert len(products) == 1  # Only the valid product should be included
    assert products[0]["name"] == "Mouse"
    mock_logger.error.assert_called_once()
    assert "Error parsing product" in mock_logger.error.call_args[0][0]


def test_empty_products():
    xml_str = """
    <sales_data date="2024-03-15">
        <products>
        </products>
    </sales_data>
    """

    with patch('src.utils.logger') as mock_logger:
        report_date, products = parse_sales_report_xml(xml_str)

    assert report_date == datetime(2024, 3, 15)
    assert products == []
    mock_logger.info.assert_called_once()
    assert "0 products" in mock_logger.info.call_args[0][0]