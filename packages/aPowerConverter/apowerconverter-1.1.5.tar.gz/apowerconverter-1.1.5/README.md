# aPowerConverter

A powerful converter from DOCX to AsciiDoc format, using Pandoc with smart processing and formatting options.

## Features

- Smart DOCX to AsciiDoc conversion
- Intelligent section number handling
- Automatic image extraction and management
- Smart table formatting with [INFO] tags
- Heading hierarchy normalization
- Document ID insertion
- Detailed logging and progress feedback
- Dry-run mode for testing
- Recursive directory processing
- Color-coded output (can be disabled)

## Requirements

### Python Requirements (automatically installed)
- Python 3.9 or higher
- pypandoc >= 1.11

### External Dependencies
- Pandoc (for conversion)
  - Download from https://pandoc.org/installing.html
  - Required for all conversions

## Installation

1. Install Python 3.9 or higher if not already installed:
   - Download from https://www.python.org/downloads/
   - Make sure to check "Add Python to PATH" during installation

2. Install Pandoc:
   - Download from https://pandoc.org/installing.html
   - Follow the installation instructions for your operating system

3. Install aPowerConverter:
   ```bash
   pip install aPowerConverter
   ```

## Usage

### Basic Usage

Convert a DOCX file to AsciiDoc:
```bash
apower-converter document.docx
```

### Advanced Options

Process multiple DOCX files:
```bash
apower-converter doc1.docx doc2.docx
```

Convert all DOCX files in a directory:
```bash
apower-converter ./documents/
```

Extract images during conversion:
```bash
apower-converter document.docx -i ./images/
```

Keep section numbers:
```bash
apower-converter document.docx -k
```

Generalize headings:
```bash
apower-converter document.docx -g
```

Save output to specific directory:
```bash
apower-converter document.docx -o ./output/
```

For more options:
```bash
apower-converter --help
```

## Features in Detail

### Smart Table Detection
Tables with empty cells in the first column are automatically marked with [INFO] tags in the AsciiDoc output.

### Image Handling
Images are extracted to a configurable directory, with each document's images placed in a subdirectory named after the document.

### Heading Normalization
The `-g` option normalizes heading levels, ensuring a consistent hierarchy starting at level 2 (==).

### Document IDs
Each converted document automatically gets a document ID based on the filename, making it easy to cross-reference documents.

## License

This project is licensed under the GNU General Public License v3 (GPLv3) - see the LICENSE file for details. 