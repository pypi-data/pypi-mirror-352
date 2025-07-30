from setuptools import setup, find_packages
from legiswebapi import __version__

setup(
    name="legisweb-api",
    version=__version__,  
    packages=find_packages(),
    install_requires=[
        "requests"
    ],
    author="Ismael Nascimento",
    author_email="ismaelnjr@icloud.com",
    description="Cliente Python para a API Legisweb",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/ismaelnjr/legisweb-api-project", 
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",  # ou outra
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
)
