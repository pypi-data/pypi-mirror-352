from notion import Client, Components, Properties
from .html import NotionBlockMapping
from .styles import Style, DefaultStyle
from .pdf import PDFConverter

from pathlib import Path
from datetime import datetime

import os

class NotionExporter:
    def __init__(self, client: Client) -> None:
        self.__notion_client = client

    def __get_pages(self, filter: str) -> list[str]:
        pages = self.__notion_client.search_pages(query=filter)
        return [page["id"] for page in pages["results"]]

    def __get_page(self, page_id: str) -> dict:
        return self.__notion_client.get_page_by_id(page_id)

    def __get_blocks(self, page: dict) -> list[dict]:
        blocks = self.__notion_client.get_block_children(page["id"])
        return [block for block in blocks["results"]]

    def export_page(self, filter: str = "", style: Style = DefaultStyle(), save_pdf: bool = True, output_dir: str = "output", create_dir: bool = True, date_based_output: bool = True) -> None:
        if date_based_output:
            output_dir = f"{output_dir}/{datetime.now().strftime('%Y-%m-%d')}"
        if create_dir:
            os.makedirs(output_dir, exist_ok=True)
        print(f"🔍 Searching for pages...")
        pages = self.__get_pages(filter)
        print(f"🔍 Found {len(pages)} pages to export!")
        for page in pages:
            page = self.__get_page(page)
            page_title = page["properties"]["Name"]["title"][0]["plain_text"]
            page_id = page["id"]
            print(f"📄 Exporting {page_title}...")
            html = "<html>"
            html += style.get_style()
            html += "<body>"
            html += f"<div class='notion-properties'>"
            html += f"<span class='notion-properties-icon'>{page['icon']['emoji']}</span>"
            html += f"<h2>{page_title}</h2>"
            html += f"</div>"
            blocks = self.__get_blocks(page)
            for block in blocks:
                mapping = NotionBlockMapping(block)
                if mapping.mapping_result():
                    html += "".join(mapping.get_html())
            html += "</body></html>"
            html = html.replace("  ", "")
            html = html.replace("\n", "")
            if save_pdf:
                self.save_pdf(html, page_id, page_title, output_dir)
            else:
                self.save_html(html, page_id, page_title, output_dir)
            print(f"✅ Exported {page_title}!")

    def save_html(self, html: str, id: str, page_title: str, output_dir: str = "output") -> None:
        print(f"💾 Saving {page_title}...")
        with open(f"{output_dir}/{page_title}_{id}.html", "w") as f:
            f.write(html)
        print(f"✅ Saved {page_title}!")

    def save_pdf(self, html: str, id: str, page_title: str, output_dir: str = "output") -> None:
        print(f"💾 Saving {page_title}...")
        convert = PDFConverter(html)
        convert.save(Path(f"{output_dir}/{page_title}_{id}.pdf"))
        print(f"✅ Saved {page_title}!")

