import logging
from typing import TYPE_CHECKING

from pyalura import utils
from pyalura.base import Base

if TYPE_CHECKING:
    from pyalura.item import Item

logger = logging.getLogger(__name__)


class Answer(Base):
    """
    Representa una respuesta individual a una pregunta de selección.

    Atributos:
        id (int): Identificador único de la respuesta.
        text (str): Texto de la respuesta.
        is_correct (bool): Indica si la respuesta es correcta.
        is_selected (bool): Indica si la respuesta ha sido seleccionada por el usuario.
        choice (Question): Objeto Question al que pertenece esta respuesta.
    """

    def __init__(
        self,
        id: int,
        text: str,
        is_correct: bool,
        is_selected: bool,
        choice: "Question",
    ):
        """
        Inicializa una nueva instancia de la clase Answer.

        Args:
            id (int): Identificador único de la respuesta.
            text (str): Texto de la respuesta.
            is_correct (bool): Indica si la respuesta es correcta.
            is_selected (bool): Indica si la respuesta ha sido seleccionada por el usuario.
            choice (Question): Objeto Question al que pertenece esta respuesta.
        """
        self.id = id
        self.text = text
        self.is_correct = is_correct
        self.is_selected = is_selected
        self.choice = choice
        super().__init__()
        logging.debug(f"Answer creada con id: {self.id}, text: '{self.text}'")

    def select(self):
        """Marca la respuesta como seleccionada."""
        self.is_selected = True
        logging.info(f"Respuesta con id: {self.id} seleccionada.")
        return self

    def unselect(self):
        """Marca la respuesta como no seleccionada."""
        self.is_selected = False
        logging.info(f"Respuesta con id: {self.id} deseleccionada.")


class Question(Base):
    """
    Representa un conjunto de respuestas posibles a una pregunta de selección.

    Atributos:
        answers (list[Answer]): Lista de objetos Answer que son las opciones de respuesta.
        parent (Item): Objeto Item (pregunta) al que pertenece este conjunto de opciones.
    """

    def __init__(self, answers: list["Answer"], item: "Item"):
        self.answers = answers
        self.parent = item
        super().__init__()
        logging.debug(f"Question creada para el item con id: {self.parent.taks_id}")

    def send_answers(self, answers: list["Answer"]):
        """
        Selecciona y envía las respuestas.

        Desmarca todas las respuestas anteriores y marca las respuestas proporcionadas como seleccionadas.
        Luego, envía las respuestas seleccionadas al backend.

        Args:
            answers (list[Answer]): Lista de objetos Answer que se van a marcar como seleccionadas.
        """
        logging.info(
            f"Enviando respuestas para Question del item: {self.parent.taks_id}"
        )

        for answer in self.answers:
            answer.unselect()
            logging.debug(f"Respuesta con id: {answer.id} deseleccionada.")

        for answer in answers:
            answer.is_selected = True
            logging.debug(f"Respuesta con id: {answer.id} seleccionada.")

        self.send_selected_answers()

    def send_selected_answers(self):
        """
        Envía las respuestas seleccionadas al backend.

        Construye el payload JSON con las IDs de las respuestas seleccionadas y envía
        una petición POST a la URL correspondiente del backend.
        """
        logging.info(
            f"Enviando respuestas seleccionadas para Question del item: {self.parent.taks_id}"
        )
        answers = []
        alternatives = []
        for answer in self.answers:
            if answer.is_selected:
                answers.append(answer)
                logging.debug(f"Respuesta con id: {answer.id} seleccionada.")

        for answer in answers:
            alternatives.append(answer.id)

        json_data = {
            "taskId": self.parent.taks_id,
            "alternatives": alternatives,
        }

        section_index = self.parent.section.index.lstrip("0")
        choice_type = "singlechoice" if self.is_single_question else "multiplechoice"
        course_url = self.parent.section.course.url_base
        url = f"{course_url}/section/{section_index}/{choice_type}/answer"

        logging.debug(f"URL para enviar las respuestas: {url}, data: {json_data}")
        self._make_request(url, method="POST", json=json_data)
        logging.info(
            f"Respuestas enviadas correctamente para Question del item: {self.parent.taks_id}"
        )

    def get_selected_answers(self) -> list["Answer"]:
        """
        Obtiene las respuestas actualmente seleccionadas.

        Returns:
            list[Answer]: Lista de objetos Answer que están seleccionados.
        """
        selected_answers = [answer for answer in self.answers if answer.is_selected]
        logging.debug(
            f"Respuestas seleccionadas obtenidas: {[answer.id for answer in selected_answers]} para Question del item: {self.parent.taks_id}"
        )
        return selected_answers

    def resolve(self) -> bool:
        for answer in self.answers:
            if answer.is_correct:
                answer.select()
        return self.send_selected_answers()

    @property
    def is_single_question(self) -> bool:
        """
        Verifica si el tipo de pregunta es de opción única.

        Returns:
            bool: True si el tipo es de opción única, False de lo contrario.
        """
        is_single = (
            self.parent.type == utils.ArticleType.SINGLE_CHOICE
            or self.parent.type == utils.ArticleType.PRACTICE_CLASS_CONTENT
        )
        logging.debug(
            f"Question del item: {self.parent.taks_id} es de tipo singlechoice: {is_single}"
        )
        return is_single

    @property
    def is_multiple_question(self) -> bool:
        """
        Verifica si el tipo de pregunta es de opción múltiple.

        Returns:
            bool: True si el tipo es de opción múltiple, False de lo contrario.
        """
        is_multiple = self.parent.type == utils.ArticleType.MULTIPLE_CHOICE
        logging.debug(
            f"Question del item: {self.parent.taks_id} es de tipo multiplechoice: {is_multiple}"
        )
        return is_multiple
