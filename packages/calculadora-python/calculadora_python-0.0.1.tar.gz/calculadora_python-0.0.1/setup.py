from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as f:
    page_description = f.read()

with open("requirements.txt") as f:
    requirements = f.read().splitlines()

setup(
    name="calculadora-python",
    version="0.0.1",
    author="Juan da Mata",
    author_email="juandamata2000@hotmail.com",
    description="Uma calculadora simples feita com python",
    long_description=page_description,
    long_description_content_type="text/markdown",
    url="https://github.com/JuanDaMata/simple-package-template",
    packages=find_packages(),
    install_requires=requirements,
    license="MIT",
    python_requires='>=3.8',
)