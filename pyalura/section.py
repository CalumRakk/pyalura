from typing import TYPE_CHECKING

from pyalura import utils
from pyalura.base import Base
from pyalura.item import Item

if TYPE_CHECKING:
    from pyalura import Course


class Section(Base):
    def __init__(self, name, url, course: "Course"):
        index, title = name.split(".", 1)
        self.index = index  # indice de la sección, empieza en 1.
        self.title = title.strip()
        self.url = url
        self.course = course
        super().__init__()

    @property
    def items(self) -> list[Item]:
        if hasattr(self, "_items") is False:
            root = self._fetch_root(self.url)
            items = [Item(**i, section=self) for i in utils.get_items(root)]
            setattr(self, "_items", items)
        return getattr(self, "_items")

    @property
    def index_last_section(self) -> int:
        return self.course.index_last_section

    @property
    def is_last_section(self) -> bool:
        if hasattr(self, "_is_last_section") is False:
            is_last_section = self.index == self.index_last_section
            setattr(self, "_is_last_section", is_last_section)
        return getattr(self, "_is_last_section")
