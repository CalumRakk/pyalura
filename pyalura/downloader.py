import logging
import random
from pathlib import Path
from typing import Union

from pyalura.item import Item
from pyalura.utils import sleep_progress

logger = logging.getLogger(__name__)


class Downloader:
    def __init__(self, base_folder: Union[str, Path]):
        self.base_folder = (
            Path(base_folder) if isinstance(base_folder, str) else base_folder
        )

    def _get_output_path(self, item: Item) -> Path:
        """Calcula la ruta de guardado basada en la estructura del item."""
        course = item.section.course
        section = item.section

        course_path = self.base_folder / course.subcategory / course.title_slug
        section_path = course_path / f"{section.index}-{section.title_slug}"
        item_path = section_path / f"{item.index}-{item.title_slug}"

        item_path.parent.mkdir(parents=True, exist_ok=True)
        return item_path

    def download_item(self, item: Item):
        """Descarga el contenido del item usando la lógica encapsulada."""
        output_path = self._get_output_path(item)

        final_path = output_path.with_suffix(".mp4" if item.is_video else ".md")

        if final_path.exists():
            logger.info(f"El item {item.title} ya existe en {final_path}")
            return

        logger.info(f"Descargando Item: {item.index} - {item.title}")
        content = item.get_content()

        if item.is_video:
            download_url = content["videos"]["hd"]["mp4"]

            response = item.get_resource_stream(download_url)
            with open(final_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)

        else:
            final_path.write_text(content["content"], encoding="utf-8")

        sleep_progress(random.randint(5, 15))
