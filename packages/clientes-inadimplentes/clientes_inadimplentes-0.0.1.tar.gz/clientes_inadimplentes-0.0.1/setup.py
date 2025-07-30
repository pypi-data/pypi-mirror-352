from setuptools import setup, find_packages

with open("README.md", "r") as f:
    page_description = f.read()

with open("requirements.txt") as f:
    requirements = f.read().splitlines()

setup(
    name="clientes_inadimplentes",
    version="0.0.1",
    author="ArturJBraga",
    author_email="mr.arturj@gmail.com",
    description="Criar função para descobrir os clientes inadimplentes de uma empresa",
    long_description=page_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ArturJBraga/clientes_inadimplentes.git",
    packages=find_packages(),
    install_requires=requirements,
    python_requires='>=3.5',
)