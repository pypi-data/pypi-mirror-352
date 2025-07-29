from .heading import NotionHeading
from .paragraph import NotionParagraph
from .callout import NotionCallout

class NotionBlockMapping:
    def __init__(self, data: dict) -> None:
        self.__data = data
        self.__notion_block = self.__mapping()

    def mapping_result(self) -> bool:
        return self.__notion_block is not None

    def __get_block_type(self) -> str:
        return self.__data["type"]
    
    def __mapping(self) -> None:
        block_type = self.__get_block_type()
        match block_type:
            case "heading_1" | "heading_2" | "heading_3":
                level = block_type.split("_")[1]
                return NotionHeading(self.__data, level)
            case "paragraph":
                return NotionParagraph(self.__data)
            case "callout":
                return NotionCallout(self.__data)
            case _:
                return None
    
    def get_html(self) -> list[str]:
        return self.__notion_block.get_html()