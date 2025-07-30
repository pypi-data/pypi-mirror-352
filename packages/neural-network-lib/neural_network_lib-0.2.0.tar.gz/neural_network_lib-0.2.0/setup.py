from pathlib import Path
from setuptools import setup, find_packages

current_dir = Path(__file__).parent
long_description = (current_dir / "README.md").read_text(encoding="utf-8")

setup(
    name="neural-network-lib",
    version="0.2.0",
    author="Тихонов Иван",
    author_email="tihonovivan737@gmail.com",
    description="Легковесная библиотека для создания и обучения нейронных сетей с GPU-ускорением",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    python_requires=">=3.6",
)