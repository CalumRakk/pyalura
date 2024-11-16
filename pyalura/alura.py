import requests
import pyalura.utils as utils
from lxml import html


class Base:
    def _make_request(self, url):
        response = requests.get(
            url,
            cookies=utils.cookies,
            headers=utils.headers,
        )
        response.raise_for_status()
        return response

    def _get_root(self, url):
        response = self._make_request(url)
        return html.fromstring(response.text)


class Alura(Base):

    def __init__(self, url):
        self.url_origin = url

    def iter_course(self):
        url_main_curso = utils.remove_paths(self.url_origin)
        url_course = utils.get_redirection(url_main_curso)

        root = self._get_root(url_course)
        course_content = utils.get_course_content(root)
        for icontent in course_content:
            print(icontent["name"])
            items = utils.get_items(root)

            for item in items:
                item_url = item["url"]

                print("\t", f"{item['index']} {item['title']} - {item['type']}")

                item_response = self._make_request(item_url)
                item_root = html.fromstring(item_response.text)

                item_video = None
                item_content = None
                item_raw_html = item_response.text
                if item["type"] == utils.ArticleType.VIDEO:
                    item_video = utils.get_item_video(item_url)
                    item_content = utils.get_item_content(item_root)
                else:
                    item_content = utils.get_item_content(root)

                item.update(
                    {
                        "video": item_video,
                        "content": item_content,
                        "raw_html": item_raw_html,
                        "section": icontent,
                    }
                )
                yield item
