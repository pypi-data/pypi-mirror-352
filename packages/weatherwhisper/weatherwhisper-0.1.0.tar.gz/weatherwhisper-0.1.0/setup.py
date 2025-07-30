from setuptools import setup, find_packages
import os

# Read the contents of the README file
with open("README.md", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="weatherwhisper",
    version="0.1.0",
    description="A command-line tool for fetching and displaying weather information",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Danush Gopinath",
    author_email="danushgopinath8502@gmail.com",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "click",
        "requests",
        "colorama",
        "tabulate",
        "configparser",
    ],
    entry_points={
        "console_scripts": [
            "weatherwhisper=weatherwhisper.cli:main",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
    python_requires=">=3.6",
    keywords="weather, cli, openweathermap, forecast, terminal",
    project_urls={
        "Homepage": "https://github.com/danushgopinath/weatherwhisper",
        "Bug Tracker": "https://github.com/danushgopinath/weatherwhisper/issues",
    },
    license_files=("LICENSE",),
)