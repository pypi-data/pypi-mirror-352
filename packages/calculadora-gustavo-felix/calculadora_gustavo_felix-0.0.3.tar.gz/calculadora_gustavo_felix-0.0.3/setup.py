from setuptools import setup, find_packages # type: ignore

with open("README.md", "r") as f:
    page_description = f.read()

with open("requirements.txt") as f:
    requirements = f.read().splitlines()

setup(
    name="calculadora-gustavo-felix",
    version="0.0.3",
    author="Gustavo Felix",
    author_email="gustavofelix2007@gmail.com",
    description="Uma simples calculadora.",
    long_description=page_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Gustavo-Felix/simple-package-template",
    packages=find_packages(),
    install_requires=requirements,
    python_requires='>=3.8'
)