from setuptools import setup, find_packages

# Función para leer la versión desde __init__.py
def get_version():
    version_file = "babot/__init__.py"
    with open(version_file, "r", encoding="utf-8") as f:
        for line in f:
            if line.startswith("__version__"):
                delim = '"' if '"' in line else "'"
                return line.split(delim)[1]
    raise RuntimeError("No se pudo encontrar la versión.")

setup(
    name="babot",  # Nombre del paquete
    version=get_version(),
    description="Framework para crear agentes inteligentes personalizados",
    long_description=open("README.md", "r", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="Kevin Turkienich",
    author_email="kevin_turkienich@outlook.com",
    url="https://github.com/Excel-ente/babot",  # Repositorio del proyecto
    packages=find_packages(),
    include_package_data=True,
    package_data={
        "babot": [
            "template/*",
            "template/**/*", 
            "main.py"
        ],
    },
    install_requires=[
        "rich>=13.9.0",
        "pyyaml>=6.0",
        "python-dotenv>=1.0.0",
    ],
    extras_require={
        "agents": [
            "langchain-ollama>=0.2.2",
            "pypdf>=5.1.0",
            "pytesseract>=0.3.13",
            "pdf2image>=1.17.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "babot=babot.cli:main",  # CLI principal
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
)
