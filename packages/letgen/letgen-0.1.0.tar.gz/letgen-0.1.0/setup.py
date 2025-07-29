from setuptools import setup, find_packages

setup(
    name="letgen",
    version="0.1.0",
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
)