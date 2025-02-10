import argparse
import json
import logging
import os

import xmltodict


logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger()


def validate_product(product):
    try:
        required_fields = ["id", "name", "price", "category"]
        for field in required_fields:
            if field not in product:
                raise ValueError(f"Missing required field: {field}")

        product_id = str(product.get("id", "")).strip()
        if not product_id.isdigit():
            raise ValueError(f"id '{product_id}' must be a number.")

        price = str(product.get("price", "")).strip()
        price = float(price)
        if price <= 0:
            raise ValueError(f"Price '{price}' must be greater than 0")

        name = product.get("name", "").strip()
        if not name:
            raise ValueError("Product 'name' cannot be empty.")

        category = product.get("category", "").strip()
        if not category:
            raise ValueError("Product 'category' cannot be empty.")

        return True
    except ValueError as e:
        logger.error(f"Validation error: {e}")
        return False


def parse_product(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            data = xmltodict.parse(file.read())

        product_dict = data.get("product", {})

        if validate_product(product_dict):
            return product_dict
        else:
            raise ValueError(f"Invalid product data in {file_path}")
    except Exception as e:
        raise ValueError(f"Error parsing {file_path}: {e}")


def write_xml_to_json(xml_file, output_dir):
    try:
        product_dict = parse_product(xml_file)
        json_file = os.path.join(
            output_dir, os.path.basename(xml_file).replace(".xml", ".json")
        )
        with open(json_file, "w", encoding="utf-8") as f:
            json.dump(product_dict, f, indent=4)
        logger.info(f"Successfully converted {xml_file} to {json_file}")

    except ValueError as e:
        logger.warning(f"Skipping invalid file: {xml_file} | Error: {e}")
    except Exception as e:
        logger.error(
            f"Exception while converting {os.path.basename(xml_file)}: {e}"
        )


def convert_all_data(input_dir, output_dir):
    if not os.path.exists(input_dir):
        logger.error(f"Input directory doesn't exist: {input_dir}")
        return

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    xml_files = [
        file for file in os.listdir(input_dir) if file.endswith(".xml")
    ]

    if not xml_files:
        logger.warning(f"There are no xml files in {input_dir}")
        return

    for filename in xml_files:
        write_xml_to_json(os.path.join(input_dir, filename), output_dir)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert xml to Json")
    parser.add_argument("--input-dir", required=True, help="Path to xml files")
    parser.add_argument(
        "--output-dir", required=True, help="Path to save converted files"
    )

    args = parser.parse_args()

    convert_all_data(args.input_dir, args.output_dir)
