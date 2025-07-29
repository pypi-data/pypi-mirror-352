from setuptools import setup, find_packages

with open("README.md", "r") as f:
    page_description = f.read()

with open("requirements.txt") as f:
    requirements = f.read().splitlines()

setup(
    name="landau-image-processing",
    version="0.0.1",
    author="Yury Landau",
    author_email="yurylandau@gmail.com",
    description="My short description",
    
    # Adiciona uma descrição longa ao pacote
    # Isso é útil para fornecer mais informações sobre o pacote
    # e pode ser exibido em repositórios como o PyPI.
    # O conteúdo da descrição longa pode ser escrito em Markdown
    # ou reStructuredText, dependendo do que você preferir.
    # Aqui, estamos usando o conteúdo do arquivo README.md como descrição longa.
    long_description=page_description,
    long_description_content_type="text/markdown",
    url="https://github.com/YuryLandau/image-processing-package",
    
    # Especifica os pacotes a serem incluídos
    # Se você não quiser incluir todos os pacotes, pode usar find_packages(exclude=["tests*"])
    packages=find_packages(),

    # Instala dependências, caso o pacote tenha dependências de outros pacotes.
    install_requires=requirements,
    python_requires='>=3.10',
)