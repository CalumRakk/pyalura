from lxml import html
import html2text


def _convert_html_to_markdown(self, html_content: bytes, header: str) -> str:
    """
    Convierte el contenido HTML a formato Markdown.
    """
    string = html2text.html2text(html_content.decode("UTF-8"))
    return f"# {header}\n\n{string}"


def get_answers(root) -> dict:
    """
    Extrae y convierte el contenido HTML de un episodio/tarea en formato Markdown.
    """
    choices = []
    for element in root.xpath(".//div[@class='container']/form/li"):
        choice_id = element.get("data-alternative-id")
        is_correct = element.get("data-correct").strip().lower() in ("true", "yes", "1")
        element_to_string = html.tostring(element.find(".//p"))
        choice_text = html2text.html2text(element_to_string.decode("UTF-8"))
        is_selected = "alternativeList-item--checked" in element.get("class")
        choices.append(
            {
                "id": choice_id,
                "text": choice_text,
                "is_correct": is_correct,
                "is_selected": is_selected,
            }
        )
    return choices
