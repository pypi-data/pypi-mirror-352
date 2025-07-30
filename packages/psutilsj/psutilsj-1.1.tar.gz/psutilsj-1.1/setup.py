from setuptools import setup, find_packages

setup(
    name="psutilsj",
    version="1.1",
    description="CLI tool to SSH and run j.py",
    author="ubuntu",
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "lz=utilslz.cli:main",
        ],
    },
    python_requires=">=3.6",
)
