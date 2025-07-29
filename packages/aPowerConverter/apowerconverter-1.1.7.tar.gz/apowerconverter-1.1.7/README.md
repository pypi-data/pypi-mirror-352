# aPowerConverter

A powerful tool to convert DOCX files to AsciiDoc format with special handling for tables and formatting.

## Features

- Converts DOCX files to AsciiDoc format using Pandoc
- Special handling for tables with `|a|` format, converting them to INFO blocks
- Preserves document structure and formatting
- Supports batch processing of multiple files
- Handles images and media extraction
- Normalizes punctuation and heading levels
- Supports document ID generation

## Installation

Make sure you have Python 3.6+ and Pandoc installed on your system.

```bash
pip install aPowerConverter
```

## Usage

Basic usage:
```bash
aPowerConverter input.docx
```

Convert multiple files:
```bash
aPowerConverter file1.docx file2.docx file3.docx
```

Options:
- `-o, --output-dir`: Output directory for converted files
- `-i, --image-dir`: Base directory for extracted images
- `-k, --keep-numbers`: Keep section numbers from the original document
- `-d, --dry-run`: Show what would be done without making changes
- `-q, --quiet`: Suppress progress messages
- `-g, --generalize`: Generalize headings after conversion
- `-v, --version`: Show version information

## Table to INFO Block Conversion

The converter automatically detects tables with `|a|` format and converts them to INFO blocks:

Input table:
```
|===
| a|
* First bullet point
* Second bullet point
|===
```

Gets converted to:
```
[INFO]
====
* First bullet point
* Second bullet point
====
```

## Requirements

- Python 3.6+
- Pandoc (https://pandoc.org/installing.html)

## License

MIT License 