from setuptools import setup, find_packages

with open("README.md", "r") as f:
    page_description = f.read()

with open("requirements.txt") as f:
    requirements = f.read().splitlines()

setup(
    name="pacote_testpy_dio",
    version="0.0.2",
    author="Douglas",
    author_email="douglasalvesmoreira2013@gmail.com",
    description="Frase simples para progressão de aprendizado",
    long_description=page_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Douglas-A-M/simple-package-template",
    packages=find_packages(),
    install_requires=requirements,
    python_requires='>=3.8',
)