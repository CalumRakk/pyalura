import json
import logging
from pathlib import Path
from typing import List, Union

from pyalura.course import Course
from pyalura.item import Item
from pyalura.utils import sleep_progress

logger = logging.getLogger(__name__)


class Downloader:
    def __init__(self, base_folder: Union[str, Path]):
        self.base_folder = (
            Path(base_folder) if isinstance(base_folder, str) else base_folder
        )
        self.base_folder.mkdir(parents=True, exist_ok=True)
        self.history_file = self.base_folder / "cursos_descargados.json"

    def _get_output_path(self, item: Item) -> Path:
        """Calcula la ruta de guardado."""
        course = item.section.course
        section = item.section
        course_path = self.base_folder / course.subcategory / course.title_slug
        section_path = course_path / f"{section.index}-{section.title_slug}"
        item_path = section_path / f"{item.index}-{item.title_slug}"
        item_path.parent.mkdir(parents=True, exist_ok=True)
        return item_path

    def _load_history(self) -> List[str]:
        if self.history_file.exists():
            return json.loads(self.history_file.read_text())
        return []

    def _save_history(self, url: str):
        history = self._load_history()
        if url not in history:
            history.append(url)
            self.history_file.write_text(json.dumps(history, indent=2))

    def download_item(self, item: Item):
        """Descarga un item individual."""
        output_path = self._get_output_path(item)
        final_path = output_path.with_suffix(".mp4" if item.is_video else ".md")

        if final_path.exists():
            logger.info(f"Omitiendo {item.title}, ya existe.")
            return

        logger.info(f"Descargando: {item.title}")
        try:
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

            sleep_progress(3)

        except Exception as e:
            logger.error(f"Error descargando {item.title}: {e}")

    def download_course(self, url: str):
        """Descarga un curso completo."""
        history = self._load_history()
        if url in history:
            logger.info(f"Curso ya descargado anteriormente: {url}")
            return

        logger.info(f"Iniciando descarga del curso: {url}")
        course = Course(url)
        try:
            for item in course.iter_items():
                self.download_item(item)

            self._save_history(url)
            logger.info(f"Curso completado: {course.title}")

        except Exception as e:
            logger.error(f"Error descargando el curso {course.title}: {e}")

    def download_list(self, urls: list[str]):
        """Descarga una lista de URLs."""
        urls = list(set(u for u in urls if u.strip()))
        for url in urls:
            self.download_course(url)
