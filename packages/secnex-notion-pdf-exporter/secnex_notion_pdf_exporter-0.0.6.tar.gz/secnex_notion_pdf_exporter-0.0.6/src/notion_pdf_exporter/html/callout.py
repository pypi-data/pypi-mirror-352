class NotionCallout:
    def __init__(self, data: dict) -> None:
        self.__data = data
        self.__text = self.__data["callout"]["rich_text"]
        self.__icon = self.__data["callout"]["icon"]["emoji"]

    def get_text(self, text: list[dict]) -> list[str]:
        return [t["plain_text"] for t in text]
    
    def get_html(self) -> list[str]:
        text = self.get_text(self.__text)
        return [f"<div class='notion-callout'><div class='notion-callout-icon'>{self.__icon}</div><div class='notion-callout-text'>{t}</div></div>" for t in text]
    