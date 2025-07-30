from setuptools import setup, find_packages

with open("README.md", "r") as f:
    descricao = f.read()

setup(
    name="text-utils-tania-pypi",
    version="0.0.1",
    author="tania.cremonini",
    author_email="taninha_cremonini@hotmail.com",
    description="Funções simples para manipulação de texto",
    long_description=descricao,
    long_description_content_type="text/markdown",
    url="https://github.com/seuusuario/text-utils",
    packages=find_packages(),
    install_requires=[],
    python_requires='>=3.6',
)


