from setuptools import setup, find_packages

setup(
    name="binary_gurdeep",
    version="0.1.0",
    author="Gurdeep",
    author_email="gurdeep@example.com",
    description="A simple binary arithmetic library using 2's complement",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/gurdeep/binary_gurdeep",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
