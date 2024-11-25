from pyalura.base import Base
from pyalura.item import Item
from pyalura import utils

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pyalura import Course


class Section(Base):
    def __init__(self, name, url, course: "Course"):
        index, title = name.split(".", 1)
        self.index = index
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
