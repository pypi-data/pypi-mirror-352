from setuptools import setup
import os

def read_file(file_name):
    """Read a file with UTF-8 encoding, return empty string if not found."""
    if os.path.exists(file_name):
        with open(file_name, encoding="utf-8") as f:
            return f.read()
    return ""

setup(
    name="gccdpune",
    version="1.0.2",
    py_modules=["gccdpune"],
    entry_points={"console_scripts": ["gccdpune=gccdpune:main"]},
    description="Interactive CLI for Google Cloud Community Day Pune 2025",
    long_description=read_file("README.md"),
    long_description_content_type="text/markdown",
    author="Gitesh Mahadik",
    author_email="gmahadik8080@gmail.com",
    url="https://github.com/Gitesh08/gccdpune",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    install_requires=["colorama>=0.4.6"],
)
