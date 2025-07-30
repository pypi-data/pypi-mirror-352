from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="code-printer",
    version="1.0.3",
    author="Shriyans",
    author_email="your.email@example.com",
    description="A global Python package to print predefined code snippets",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/MrPhantom2325/code-printer.git",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
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
    entry_points={
        "console_scripts": [
            "code-printer=code_printer.cli:main",
            "codeprint=code_printer.cli:main",  # Shorter alias
        ],
    },
    install_requires=[
        # Add any dependencies here
    ],
)