# setup.py
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="laserfocus",  # Replace with your package name
    use_scm_version=True,
    setup_requires=['setuptools_scm'],
    author="laserfocus",
    author_email="aa@laserfocus.space",
    description="A collection of utilities for laserfocus",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/laserfocus/pip",  # Optional: GitHub URL
    packages=find_packages(),  # Automatically finds your package
    install_requires=[
        "Requests==2.32.3",
        "certifi==2024.7.4",
        "charset-normalizer==3.4.1",
        "idna==3.10",
        "markdown-it-py==3.0.0",
        "mdurl==0.1.2",
        "Pygments==2.19.1",
        "urllib3==2.3.0",
        "rich==13.9.3",
        "SQLAlchemy==2.0.35",
        "beautifulsoup4==4.12.3",
        "soupsieve==2.6",
        "typing_extensions==4.12.2"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",  # Specify compatible Python versions
)