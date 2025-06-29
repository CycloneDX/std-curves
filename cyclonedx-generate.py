#!/usr/bin/env python3
"""
Generate Summary Script

This script generates a summary JSON file containing essential information about elliptic curves
from various categories, and updates the CurveEnum in the schema file with all curves in the
format "category/name".

The script:
1. Reads all curve files from each category directory
2. Extracts the necessary information for the summary (name, desc, oid, form, aliases)
3. Generates the summary JSON in the format defined by summary_schema.json
4. Updates the CurveEnum in summary_schema.json with all curves in the format "category/name"

Usage:
    python3 generate_summary.py

Output:
    - sample_summary.json: Contains the summary information for all curves
    - summary_schema.json: Updated with all curves in the CurveEnum
"""

import os
import json
import glob

def main():
    # Define the output files
    summary_output_file = "cryptography-curves.json"
    schema_output_file = "cryptography-curves.schema.json"

    # Read the current schema
    with open(schema_output_file, 'r') as f:
        schema = json.load(f)

    # Initialize the summary structure
    summary = {
        "name": "CycloneDX Cryptography: Standard Curves",
        "description": "Information for standard elliptic curves from various categories.",
        "categories": []
    }

    # Initialize a set to collect all curve enums
    curve_enums = set()

    # Get all category directories (exclude hidden directories and files)
    category_dirs = [d for d in os.listdir('.') if os.path.isdir(d) and not d.startswith('.')]

    # Process each category directory
    for category_dir in category_dirs:
        # Look for curves.json file in the category directory
        curves_file = os.path.join(category_dir, "curves.json")
        if not os.path.exists(curves_file):
            continue

        # Read the curves file
        with open(curves_file, 'r') as f:
            category_data = json.load(f)

        # Create a category entry for the summary
        category_summary = {
            "name": category_dir.lower(),
            "description": category_data.get("desc") if category_data.get("desc") else None,
            "curves": []
        }

        # Process each curve in the category
        for curve in category_data.get("curves", []):
            # Extract the necessary information for the summary
            curve_summary = {
                "name": curve.get("name", None),
                "description": curve.get("desc") if curve.get("desc") else None,
                "oid": curve.get("oid", None),
                "form": curve.get("form", None)
            }

            # Add the curve to the curve_enums set
            curve_enum = f"{category_dir.lower()}/{curve.get('name', '')}"
            curve_enums.add(curve_enum)

            # Process aliases
            aliases = curve.get("aliases", [])
            if aliases:
                curve_summary["aliases"] = []
                for alias in aliases:
                    # Parse the alias string (format: "category/name")
                    parts = alias.split('/')
                    if len(parts) == 2:
                        alias_category, alias_name = parts
                        curve_summary["aliases"].append({
                            "category": alias_category,
                            "name": alias_name
                        })

            # Add the curve summary to the category
            category_summary["curves"].append(curve_summary)

        # Sort the curves within the category by name
        if category_summary["curves"]:
            category_summary["curves"] = sorted(category_summary["curves"], key=lambda x: x["name"])
            summary["categories"].append(category_summary)

    # Sort the categories by name
    summary["categories"] = sorted(summary["categories"], key=lambda x: x["name"])

    # Update the CurveEnum in the schema
    schema["definitions"]["CurveEnum"]["enum"] = sorted(list(curve_enums))

    # Write the updated summary to the output file
    with open(summary_output_file, 'w') as f:
        json.dump(summary, f, indent=2)

    # Write the updated schema to the output file
    with open(schema_output_file, 'w') as f:
        json.dump(schema, f, indent=2)

    print(f"Summary written to {summary_output_file}")
    print(f"Schema updated in {schema_output_file}")
    print(f"Found {len(curve_enums)} unique curves")

if __name__ == "__main__":
    main()
