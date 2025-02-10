import json
import logging
import pytest

import convert_xml_to_json


@pytest.mark.parametrize(
    "product, expected",
    [
        (
            {
                "id": "123",
                "price": "599.99",
                "name": "test",
                "category": "test",
            },
            True,
        ),
        (
            {"id": "abc", "price": "100", "name": "test", "category": "test"},
            False,
        ),
        (
            {"id": "456", "price": "-50", "name": "test", "category": "test"},
            False,
        ),
        (
            {"id": "789", "price": "0", "name": "test", "category": "test"},
            False,
        ),
        (
            {"id": "", "price": "100", "name": "test", "category": "test"},
            False,
        ),
        (
            {"id": "111", "price": "100", "name": "", "category": "test"},
            False,
        ),
        (
            {"id": "111", "price": "100", "name": "test", "category": ""},
            False,
        ),
    ],
)
def test_validate_product_logging(caplog, product, expected):
    with caplog.at_level(logging.ERROR):
        result = convert_xml_to_json.validate_product(product)
    assert result == expected
    if not expected:
        assert "Validation error" in caplog.text


@pytest.fixture
def sample_xml_file(tmp_path):
    content = """<?xml version="1.0" encoding="UTF-8"?>
    <product>
        <id>123</id>
        <name>Smartphone</name>
        <price>599.99</price>
        <category>Electronics</category>
    </product>"""
    xml_file = tmp_path / "test_product.xml"
    xml_file.write_text(content, encoding="utf-8")
    return xml_file


def test_parse_product_invalid_data(sample_xml_file):
    bad_content = """<?xml version="1.0" encoding="UTF-8"?>
    <product>
        <id>10</id>
        <price>20.89</price>
    </product>"""
    sample_xml_file.write_text(bad_content, encoding="utf-8")

    with pytest.raises(ValueError):
        convert_xml_to_json.parse_product(sample_xml_file)


def test_write_xml_to_json(sample_xml_file, tmp_path):
    output_dir = tmp_path / "output"
    output_dir.mkdir()

    convert_xml_to_json.write_xml_to_json(sample_xml_file, output_dir)

    json_file = output_dir / "test_product.json"
    assert json_file.exists()

    with open(json_file, "r", encoding="utf-8") as file:
        data = json.load(file)

    expected = {
        "id": "123",
        "name": "Smartphone",
        "price": "599.99",
        "category": "Electronics",
    }
    assert data == expected


def test_process_directory(tmp_path):
    input_dir = tmp_path / "input"
    output_dir = tmp_path / "output"
    input_dir.mkdir()
    output_dir.mkdir()

    xml_content = """<?xml version="1.0" encoding="UTF-8"?>
    <product>
        <id>124</id>
        <name>Tablet</name>
        <price>399.99</price>
        <category>Electronics</category>
    </product>"""

    xml_file = input_dir / "product.xml"
    xml_file.write_text(xml_content, encoding="utf-8")

    convert_xml_to_json.convert_all_data(input_dir, output_dir)

    json_file = output_dir / "product.json"
    assert json_file.exists()

    with open(json_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    expected = {
        "id": "124",
        "name": "Tablet",
        "price": "399.99",
        "category": "Electronics",
    }
    assert data == expected
