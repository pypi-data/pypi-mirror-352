import xml.etree.ElementTree  # nosec


class Page:
    def __init__(self, page: xml.etree.ElementTree.Element):
        self.page = page
        self.id = None
        self.title = None
        self.text = None
        self.parse()

    def parse(self) -> None:
        for child in self.page:
            child_tag = child.tag.split("}")[1] if "}" in child.tag else child.tag
            if child_tag == "title":
                self.title = child.text
            if child_tag == "id":
                self.id = child.text
            if child_tag == "revision":
                for grand_child in child:
                    grand_child_tag = grand_child.tag.split("}")[1] if "}" in grand_child.tag else grand_child.tag
                    if grand_child_tag == "text":
                        self.text = grand_child.text or ""  # there are empty pages

    @property
    def is_category(self):
        return self.title.lower().split(":")[0] == "κατηγορία" if self.title is not None else False

    def __str__(self):
        return self.title
