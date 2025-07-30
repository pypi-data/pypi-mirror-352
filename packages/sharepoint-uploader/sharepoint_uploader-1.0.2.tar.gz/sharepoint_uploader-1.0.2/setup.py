from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="sharepoint-uploader",
    version="1.0.2",
    author="Rizwana",
    author_email="rizwana@thefruitpeople.ie",
    description="A Python package for uploading files to SharePoint",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://https://github.com/The-Fruit-People/Sharepoint_uploader_pckg",
    packages=find_packages(),
    install_requires=[
        "requests>=2.25.1",
        "msal>=1.16.0",
        "pandas>=1.2.0;python_version<'3.8'",
        "pandas>=1.3.0;python_version>='3.8'",
    ],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
)