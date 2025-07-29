from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="letgen",
    version="0.1.1",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "click",
        "rich",
        "requests",
    ],
    entry_points={
        "console_scripts": [
            "letgen=cli:main",
        ],
    },
    python_requires=">=3.7",
    author="Carlos Vinicius",
    description="Gere testes automatizados em Python usando IA e linguagem natural",
    long_description=long_description,  
    long_description_content_type="text/markdown", 
    url="https://github.com/CarlossViniciuss/let", 
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Testing",
        "Intended Audience :: Developers",
    ],
)
