from pyalura.downloader import Downloader

URLTEXT = """
https://app.aluracursos.com/course/comandos-dml-manipulacion-datos-mysql
https://app.aluracursos.com/course/certificacion-oracle-cloud-infrastructure-gestion-datos-seguridad-gobernanza
https://app.aluracursos.com/course/low-code-ia-oracle-apex
"""

urls = [i.strip() for i in URLTEXT.split("\n")]
downloader = Downloader(base_folder="Descargas")
downloader.download_list(urls)
