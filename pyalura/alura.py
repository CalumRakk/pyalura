import requests
import pyalura.utils as utils
from lxml import html
import random
from datetime import datetime
import time


class Base:
    def _make_request(self, url, method="GET"):
        response = requests.request(
            method,
            url,
            cookies=utils.cookies,
            headers=utils.headers,
        )

        response.raise_for_status()
        return response

    def _fetch_root(self, url):
        response = self._make_request(url)
        return html.fromstring(response.text)


class Alura(Base):

    def __init__(self, url):
        self.url_origin = url
        self.base_course_url = utils.extract_base_url(self.url_origin)
        self.continue_course_url = utils.add_slash(self.base_course_url) + "continue/"

    @property
    def course_sections(self):
        if hasattr(self, "_course_sections") is False:
            r = self._make_request(self.continue_course_url, method="HEAD")
            url_course = r.headers["location"]
            root = self._fetch_root(url_course)
            course_sections = utils.get_course_sections(root)
            setattr(self, "_course_sections", course_sections)
        return getattr(self, "_course_sections")

    def iter_course(self):
        for course_section in self.course_sections:
            url_course = course_section["url"]
            root = self._fetch_root(url_course)
            items = utils.get_items(root)

            print(f"Seccion: {course_section['name']}")
            for item in items:
                print("\t", f"{item['index']} {item['title']} - {item['type']}")

                item_url = item["url"]
                item_response = self._make_request(item_url)
                item_root = html.fromstring(item_response.text)
                last_request_time = datetime.now()

                item_video = None
                item_content = None
                item_raw_html = item_response.text
                if item["type"] == utils.ArticleType.VIDEO:
                    item_video = utils.fetch_item_video(item_url)
                    item_content = utils.get_item_content(item_root)
                else:
                    item_content = utils.get_item_content(root)

                item.update(
                    {
                        "video": item_video,
                        "content": item_content,
                        "raw_html": item_raw_html,
                        "section": course_section,
                    }
                )
                yield item

                diff_time = datetime.now() - last_request_time
                if diff_time.total_seconds() < random.randint(5, 10):
                    time.sleep(random.randint(5, 10))
