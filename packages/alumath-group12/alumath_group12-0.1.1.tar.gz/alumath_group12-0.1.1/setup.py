from setuptools import setup, find_packages

setup(
    name="alumath_group12",  
    version="0.1.1",
    description="A simple Python library for multiplying two matrices of any size",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Yassin Hagenimna",
    author_email="hyassin509@gmail.com",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
