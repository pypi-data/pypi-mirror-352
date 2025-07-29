from setuptools import setup, find_packages

# Read the README file
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="handit-sdk",  # The name users will use to install the package
    version="1.16.0",
    description="A Python SDK for tracking Model requests and responses.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Cristhian Camilo Gomez Neira",
    author_email="cristhian@handit.ai",
    url="https://github.com/Handit-AI/handit-sdk",  # Replace with your GitHub repo
    packages=find_packages(),
    install_requires=[
        "requests>=2.31.0",
        "jsonpickle>=3.0.2",
        "aiohttp>=3.9.1",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
