#!/usr/bin/env python3
"""
Script to generate JSON schema from Pydantic models for YAML validation and IDE support.
"""

import sys
from pathlib import Path
from typing import Any, Dict
import json

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from resemu.models.resume import Resume


def generate_schema() -> Dict[str, Any]:
    """Generate JSON schema from the Resume model."""

    schema = Resume.model_json_schema()

    schema["$schema"] = "https://json-schema.org/draft/2020-12/schema"
    schema["title"] = "resemu YAML schema"
    schema["description"] = "Schema for validating resume YAML files used with resemu"

    return schema


def main() -> None:
    """Main function to generate and save the schema."""

    schema = generate_schema()

    output_dir = Path(__file__).parent.parent
    schema_file = output_dir / "schema" / "resemu.schema.json"

    schema_file.parent.mkdir(exist_ok=True)

    with open(schema_file, "w", encoding="utf-8") as f:
        json.dump(schema, f, indent=2, ensure_ascii=False)

    print(f"✅ JSON schema generated: {schema_file}")
    print(f"📊 Schema size: {schema_file.stat().st_size} bytes")


if __name__ == "__main__":
    main()
