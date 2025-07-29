from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="codexium",
    version="0.2.0",
    author="Alex Bairez",
    description="A CLI tool that automatically generates README files using AI",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/bye-rez/codexium",
    packages=find_packages(),
    py_modules=["codexium"],
    install_requires=[
        "click>=8.0.0",
        "cohere>=4.0.0",
    ],
    entry_points={
        'console_scripts': [
            'codexium=codexium:codexium',
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Documentation",
    ],
    python_requires=">=3.6",
)
