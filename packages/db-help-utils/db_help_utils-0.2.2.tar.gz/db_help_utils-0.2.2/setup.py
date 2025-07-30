from setuptools import setup, find_packages

# Чтение содержимого README.md для long_description
with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="db_help_utils",  # Имя пакета
    version="0.2.2",  # Версия
    author="ilya",
    author_email="asuslover4@gmail.com",
    description="Утилиты для работы с базами данных",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/paladinxb",  # Ссылка на репозиторий
    license="MIT",  # Лицензия
    packages=find_packages(),  # Автоматический поиск пакетов
    install_requires=[],  # Укажите зависимости, если есть
    python_requires=">=3.7",  # Минимальная версия Python
)
