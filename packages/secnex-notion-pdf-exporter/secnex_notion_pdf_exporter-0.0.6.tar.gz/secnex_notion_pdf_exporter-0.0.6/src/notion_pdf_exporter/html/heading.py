class NotionHeading:
    def __init__(self, data: dict, level: int) -> None:
        self.__data = data
        self.__level = level
        self.__text = self.__data["heading_" + level]["rich_text"]

    def get_text(self, text: list[dict]) -> list[str]:
        return [t["plain_text"] for t in text]
    
    def get_html(self) -> list[str]:
        text = self.get_text(self.__text)
        return [f"<h{self.__level}>{t}</h{self.__level}>" for t in text]
    