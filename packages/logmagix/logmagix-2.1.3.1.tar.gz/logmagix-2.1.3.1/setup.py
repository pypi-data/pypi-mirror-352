from setuptools import setup, find_packages
import os

version = {}
version_file_path = os.path.join(os.path.dirname(__file__), 'logmagix', 'version.py')
with open(version_file_path) as fp:
    exec(fp.read(), version)

setup(
    name="logmagix",
    version=version['__version__'],
    packages=find_packages(),
    install_requires=["colorama", "pystyle", "packaging"],
    author="Sexfrance",
    author_email="bwuuuuu@gmail.com",
    description="A custom logger package",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/sexfrance/LogMagix",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
