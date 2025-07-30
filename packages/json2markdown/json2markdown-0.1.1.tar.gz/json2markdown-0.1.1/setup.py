from setuptools import setup, find_packages

setup(
    name="json2markdown",
    version="0.1.1",
    packages=find_packages(),
    install_requires=[],
    description="A library to convert JSON data to Markdown documents",
    author="Govind Banura",
    author_email="govindbanura2310@gmail.com",
    license="MIT",
    url="https://github.com/govindbanura/json2markdownlib",  # Add this line
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
    ],
)
