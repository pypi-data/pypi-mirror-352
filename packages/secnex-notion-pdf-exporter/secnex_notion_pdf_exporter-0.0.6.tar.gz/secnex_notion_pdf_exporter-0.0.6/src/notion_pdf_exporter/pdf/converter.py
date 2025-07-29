from weasyprint import HTML
from pathlib import Path
import sys
import argparse

class PDFConverter:
    def __init__(self, html: str) -> None:
        self.__html = html

    def save(self, path: Path) -> None:
        HTML(string=self.__html).write_pdf(path)

    def save_to_file(self, path: Path) -> None:
        with open(path, "w") as f:
            f.write(self.__html)

def main():
    parser = argparse.ArgumentParser(description='Convert HTML to PDF')
    parser.add_argument('input', type=str, help='Input HTML file or string')
    parser.add_argument('output', type=str, help='Output PDF file path')
    parser.add_argument('--string', action='store_true', help='Treat input as HTML string instead of file')
    
    args = parser.parse_args()
    
    if args.string:
        html_content = args.input
    else:
        with open(args.input, 'r') as f:
            html_content = f.read()
    
    converter = PDFConverter(html_content)
    converter.save(Path(args.output))

if __name__ == '__main__':
    main()
