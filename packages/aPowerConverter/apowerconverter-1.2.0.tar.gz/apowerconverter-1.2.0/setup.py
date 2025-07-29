from setuptools import setup, find_packages

setup(
    name="aPowerConverter",
    version="1.2.0",
    packages=find_packages(),
    install_requires=[
        'pandoc'
    ],
    entry_points={
        'console_scripts': [
            'aPowerConverter=aPowerConverter.converter:main',
        ],
    },
    author="attoz",
    description="A tool to convert DOCX files to AsciiDoc format with special table handling",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/attoz/aPowerConverter",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
) 