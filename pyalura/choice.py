from typing import TYPE_CHECKING
from pyalura.base import Base
from pyalura import utils

if TYPE_CHECKING:
    from pyalura.item import Item


class Answer(Base):
    def __init__(self, id, text, is_correct, is_selected, choice: "Choice"):
        self.id = id
        self.text = text
        self.is_correct = is_correct
        self.is_selected = is_selected
        self.choice = choice
        super().__init__()

    def select(self):
        self.is_selected = True

    def unselect(self):
        self.is_selected = False


class Choice(Base):
    def __init__(self, answers, item: "Item"):
        self.answers = answers
        self.parent = item
        super().__init__()

    def send_answers(self, answers: list[Answer]):
        """selecciona y envias las respuestas"""
        for answer in self.answers:
            answer.is_selected = False

        for answer in answers:
            answer.is_selected = True

        self.send_selected_answers()

    # envia las respuestas seleccionadas
    def send_selected_answers(self):
        answers = []
        alternatives = []
        for answer in self.answers:
            if answer.is_selected:
                answers.append(answer)

        for answer in answers:
            alternatives.append(answer.id)

        json_data = {
            "taskId": self.parent.taks_id,
            "alternatives": alternatives,
        }

        section_index = self.parent.section.index.lstrip("0")
        choice_type = "singlechoice" if self.is_single_choice else "multiplechoice"
        course_url = self.parent.section.course.base_course_url
        url = f"{course_url}/section/{section_index}/{choice_type}/answer"

        self._make_request(url, method="POST", json=json_data)

    def get_selected_answers(self):
        return [answer for answer in self.answers if answer.is_selected]

    @property
    def is_single_choice(self):
        return self.parent.type == utils.ArticleType.SINGLE_CHOICE

    @property
    def is_multiple_choice(self):
        return self.parent.type == utils.ArticleType.MULTIPLE_CHOICE
