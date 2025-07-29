from setuptools import setup, find_packages
import os

# Read README if it exists
long_description = "Python SDK for TinyToken API"
readme_path = os.path.join(os.path.dirname(__file__), "README.md")
if os.path.exists(readme_path):
    with open(readme_path, "r", encoding="utf-8") as fh:
        long_description = fh.read()

setup(
    name="tinytoken-sdk",
    version="0.1.3",
    author="TinyToken",
    author_email="elliot@norrevik.se",
    description="Python SDK for TinyToken API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/elliot-evno/tinytoken-python-sdk",
    packages=["tinytoken"],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.7",
    install_requires=[
        "requests>=2.20.0",
    ],
    include_package_data=True,
    package_data={
        "tinytoken": ["py.typed"],
    },
) 