from setuptools import find_packages, setup

setup(
    name="pyalura",
    version="0.2.0",
    description="",
    author="Leo",
    author_email="leocasti@gmail.com",
    packages=find_packages(),
    install_requires=["lxml", "requests", "html2text", "Unidecode"],
)
