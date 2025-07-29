"""
Module for validating organisation data against the organisation schema.
"""
import json
from pathlib import Path
from typing import Any, Dict
import logging
import jsonschema
import argparse
import sys

logger = logging.getLogger(__name__)

SCHEMA_PATH = Path(__file__).parent / "schemas" / "organisation_schema.json"

def load_schema(schema_path: Path = SCHEMA_PATH) -> Dict[str, Any]:
    """
    Load a JSON schema from a file.

    Args:
        schema_path (Path): Path to the JSON schema file.

    Returns:
        Dict[str, Any]: The loaded JSON schema.
    """
    try:
        with open(schema_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Failed to load schema: {e}")
        raise

def validate_organisation(data: Dict[str, Any], schema: Dict[str, Any] | None = None) -> None:
    """
    Validate organisation data against the organisation schema.

    Args:
        data (Dict[str, Any]): The organisation data to validate.
        schema (Dict[str, Any] | None, optional): The schema to validate against. If None, loads default.

    Raises:
        jsonschema.ValidationError: If validation fails.
    """
    if schema is None:
        schema = load_schema()
    try:
        # Use jsonschema.RefResolver to resolve local references
        schema_dir = SCHEMA_PATH.parent.resolve()
        resolver = jsonschema.RefResolver(base_uri=f"file://{schema_dir}/", referrer=schema)
        jsonschema.validate(instance=data, schema=schema, resolver=resolver)
    except jsonschema.ValidationError as e:
        logger.error(f"Validation error: {e.message}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error during validation: {e}")
        raise

def main() -> None:
    """
    CLI entry point for validating organisation JSON files against the schema.
    """
    parser = argparse.ArgumentParser(
        description="Validate an organisation JSON file against the organisation schema."
    )
    parser.add_argument(
        "input",
        type=str,
        nargs="?",
        help="Path to the organisation JSON file to validate. Use '-' to read from stdin."
    )
    parser.add_argument(
        "--output-format",
        choices=["human", "json"],
        default="human",
        help="Output format: human-readable or JSON."
    )
    parser.add_argument(
        "--show-schema",
        action="store_true",
        help="Print the organisation schema and exit."
    )
    args = parser.parse_args()

    if args.show_schema:
        schema = load_schema()
        print(json.dumps(schema, indent=2))
        sys.exit(0)

    if not args.input:
        parser.error("the following arguments are required: input (unless --show-schema is used)")

    # Read input data
    try:
        if args.input == "-":
            data = json.load(sys.stdin)
        else:
            with open(args.input, "r", encoding="utf-8") as f:
                data = json.load(f)
    except Exception as e:
        logger.error(f"Failed to read input: {e}")
        if args.output_format == "json":
            print(json.dumps({"success": False, "error": str(e)}))
        else:
            print(f"[ERROR] Failed to read input: {e}")
        sys.exit(1)

    # Validate
    try:
        validate_organisation(data)
        if args.output_format == "json":
            print(json.dumps({"success": True, "message": "Validation successful."}))
        else:
            print("Validation successful.")
    except jsonschema.ValidationError as e:
        if args.output_format == "json":
            print(json.dumps({"success": False, "error": e.message}))
        else:
            print(f"[ERROR] Validation failed: {e.message}")
        sys.exit(1)
    except Exception as e:
        if args.output_format == "json":
            print(json.dumps({"success": False, "error": str(e)}))
        else:
            print(f"[ERROR] Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
