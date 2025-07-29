# setup.py
from setuptools import setup, find_packages

setup(
    name="username-checker",
    version="0.1.0",
    description="Check username availability on popular websites",
    author="Muhamadyor",
    packages=find_packages(),
    install_requires=["requests", "colorama"],
    entry_points={
        "console_scripts": [
            "username-checker=username_checker.checker:main",
        ]
    },
    python_requires=">=3.6",
)
