#! /usr/bin/env python3

from .exporter import NotionExporter
from .styles import DefaultStyle
from notion import Client

import argparse
import os

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--filter", type=str, default=os.getenv("FILTER", ""))
    parser.add_argument("--save-pdf", type=bool, default=os.getenv("SAVE_PDF", True))
    parser.add_argument("--output-dir", type=str, default=os.getenv("OUTPUT_DIR", "output"))
    parser.add_argument("--api-key", type=str, default=os.getenv("NOTION_API_KEY"))

    args = parser.parse_args()

    notion_client = Client(token=args.api_key)
    notion_exporter = NotionExporter(notion_client)

    print(f"ℹ️ Will export pages with filter: {args.filter}")
    print(f"ℹ️ Will save to directory: {args.output_dir}")

    notion_exporter.export_page(
        filter=args.filter,
        style=DefaultStyle(),
        save_pdf=args.save_pdf,
        output_dir=args.output_dir,
        create_dir=False
    )

if __name__ == "__main__":
    main()
