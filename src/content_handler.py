import json


class ContentHandler:
    content: dict

    def __init__(self, content_file_path: str):
        self.content = self.load_content(content_file_path)

    def get_section_content(self, section_name: str) -> dict | None:
        return self.content.get(section_name, None)

    def get_common_content(self) -> dict | None:
        return self.content.get('common', None)

    def load_content(self, content_file_path: str) -> dict:
        try:
            with open(content_file_path, "r") as f:
                content = json.load(f)

                return content
        except Exception as e:
            raise FileExistsError(f"Error loading content file: {e}")
