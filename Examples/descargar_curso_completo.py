from pyalura import Course
from pyalura.downloader import Downloader

url = "https://app.aluracursos.com/course/spring-boot-3-aplique-practicas-proteja-api-rest"
course = Course(url, cookies_path="app.aluracursos.com_cookies.txt")
downloader = Downloader(base_folder="Descargas")
downloader.download_course(url)
