import os
from pathlib import Path
from setuptools import setup, find_packages

# Read the contents of README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text() if (this_directory / "README.md").exists() else ""

setup(
    name="streamlit-abcjs-score",
    version="0.1.0",
    author="Kenny Zhengyang Ma",
    author_email="kenny.ma.2312@gmail.com",
    description="A Streamlit component for rendering ABC notation as musical scores using abc.js",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/zmk5566/streamlit-abcjs-score",
    packages=find_packages(),
    include_package_data=True,
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
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
        "streamlit >= 0.63",
    ],
    extras_require={
        "devel": [
            "wheel",
            "pytest>=4",
            "pytest-cov",
            "black",
        ]
    },
)
