class NotionParagraph:
    def __init__(self, data: dict) -> None:
        self.__data = data
        self.__text = self.__data["paragraph"]["rich_text"]

    def get_html(self) -> list[str]:
        text = self.get_text(self.__text)
        return [f"<p>{text[0] if text else ''}</p>"]
    
    def get_text(self, text: list[dict]) -> list[str]:
        return [t["plain_text"] for t in text]
