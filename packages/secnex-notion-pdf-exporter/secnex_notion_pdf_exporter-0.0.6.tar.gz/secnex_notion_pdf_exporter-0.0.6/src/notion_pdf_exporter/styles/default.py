from .style import Style

class DefaultStyle(Style):
    def __init__(self) -> None:
        pass
    
    def get_style(self) -> str:
        return """
        <head>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    font-size: 12px;
                    color: #000000;
                }
                .notion-properties {
                    padding: 10px;
                    border: 1px solid #EAEAEA;
                    border-radius: 5px;
                    margin-bottom: 10px;
                    display: flex;
                    align-items: center;
                    gap: 10px;
                }
                .notion-properties h2 {
                    font-size: 16px;
                    font-weight: bold;
                    margin-bottom: 10px;
                }
                .notion-properties p {
                    font-size: 12px;
                    margin-bottom: 5px;
                }
                .notion-callout {
                    padding: 10px;
                    border: 1px solid #EAEAEA;
                    border-radius: 5px;
                    margin-bottom: 10px;
                    display: flex;
                    align-items: center;
                    gap: 10px;
                }
                .notion-callout-icon {
                    font-size: 16px;
                    font-weight: bold;
                }
                .notion-callout-text {
                    font-size: 12px;
                }
            </style>
        </head>
        """