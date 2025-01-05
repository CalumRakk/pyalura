from pathlib import Path
import json
import requests
from lxml import html

headers = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "accept-language": "es,es-ES;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6,es-CO;q=0.5",
    "priority": "u=0, i",
    "sec-ch-ua": '"Not/A)Brand";v="8", "Chromium";v="126", "Microsoft Edge";v="126"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "sec-fetch-dest": "document",
    "sec-fetch-mode": "navigate",
    "sec-fetch-site": "same-origin",
    "sec-fetch-user": "?1",
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 Edg/126.0.0.0",
}


class CookieManager:

    def __init__(self):
        self.path = Path("cookies.txt")
        self.headers = headers

    def load(self):
        if self.path.exists():
            return self.path.read_text()
        raise FileNotFoundError(f"Cookie file not found: {self.path}")

    def parse_cookies(self, content, format_type="netscape"):
        cookies = {}
        if format_type == "netscape":
            for line in content.split("\n"):
                if line.startswith("#") or not line.strip():
                    continue
                fields = line.strip().split("\t")
                if len(fields) != 7:
                    raise ValueError(f"Línea malformada: {line}")
                domain, flag, path, secure, expiration, name, value = fields
                cookies[name] = {
                    "domain": domain,
                    "flag": flag == "TRUE",
                    "path": path,
                    "secure": secure == "TRUE",
                    "expiration": int(expiration) if expiration.isdigit() else None,
                    "value": value,
                }
        elif format_type == "json":
            cookies = json.loads(content)

        try:
            return {
                "SESSION": cookies.get("SESSION") or cookies["SESSION"]["value"],
                "caelum.login.token": cookies.get("caelum.login.token")
                or cookies["caelum.login.token"]["value"],
                "alura.userId": cookies.get("alura.userId")
                or cookies["alura.userId"]["value"],
            }
        except KeyError:
            return {}

    def get_cookies(self):
        content = self.load()
        if content.startswith("{"):
            return self.parse_cookies(content, format_type="json")
        elif content.startswith("["):
            return self.parse_cookies(content, format_type="json")
        else:
            return self.parse_cookies(content, format_type="netscape")

    def is_dashboard_page(self, response):
        root = html.fromstring(response.text)
        page_title = root.find(".//title").text.strip()
        return "Dashboard | Alura Latam - Cursos online de tecnologia" == page_title

    def check_cookies(self):
        cookies = self.get_cookies()

        url = "https://app.aluracursos.com/dashboard"
        response = requests.get(
            url,
            cookies=cookies,
            headers=self.headers,
        )
        if self.is_dashboard_page(response):
            return True
        return False


if __name__ == "__main__":
    cookies = CookieManager()
    print(cookies.check_cookies())
