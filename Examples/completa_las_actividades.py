from datetime import timedelta

from pyalura import Course
from pyalura.utils import sleep_progress

url = "https://app.aluracursos.com/course/consultas-sql-mysql"
curso = Course(url)
VIDEO_ESPERA = timedelta(minutes=5).total_seconds()

for section in curso.sections:
    for item in section.items:
        if item.is_marked_as_seen:
            continue
        elif item.is_video:
            item.mark_as_watched()
            sleep_progress(seconds=VIDEO_ESPERA)
        elif item.is_question:
            item.resolve_question()
            sleep_progress(seconds=60)
        else:
            item.mark_as_watched()
            sleep_progress(seconds=120)
