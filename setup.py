from setuptools import setup, find_packages

setup(
    name="aluracourse",
    version="0.1",
    description="",
    author="Leo",
    author_email="leocasti@gmail.com",
    packages=find_packages(),
    install_requires=["lxml", "requests", "html2text", "requests_cache"],
)
