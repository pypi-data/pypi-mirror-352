from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="aPowerConverter",
    version="1.1.6",
    author="attoz",
    author_email="attoz@users.noreply.github.com",
    description="A powerful converter from DOCX to AsciiDoc format using Pandoc",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/attoz/aPowerConverter",
    project_urls={
        "Bug Tracker": "https://github.com/Attoz/aPowerConverter/issues",
        "Documentation": "https://github.com/Attoz/aPowerConverter#readme",
        "Source Code": "https://github.com/Attoz/aPowerConverter",
    },
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Console",
        "Intended Audience :: End Users/Desktop",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Documentation",
        "Topic :: Office/Business",
        "Topic :: Text Processing :: Markup",
        "Topic :: Utilities",
    ],
    keywords="docx, asciidoc, converter, documentation, word, markup, text processing, pandoc",
    python_requires=">=3.9",
    install_requires=[
        "pypandoc>=1.11",  # Python interface for Pandoc
    ],
    entry_points={
        "console_scripts": [
            "apower-converter=aPowerConverter.converter:main",
        ],
    },
    package_data={
        "aPowerConverter": ["README.md"],
    },
    include_package_data=True,
) 