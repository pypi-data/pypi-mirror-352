# setup.py

from setuptools import setup, find_packages

setup(
    name="pgstudio",
    version="0.4.0",
    author="Taireru LLC",
    author_email="tairerullc@gmail.com",
    description="A GUI builder for pygame (using pygame_gui).",
    long_description=open("README.md", "r", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/TaireruLLC/pgstudio",
    packages=find_packages(),
    install_requires=[
        "pygame_gui>=0.6.0",
        "Pillow>=9.0.0"
    ],
    entry_points={
        "console_scripts": [
            "pgstudio = pgstudio.manager:main"
        ]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    license="MIT",
)
