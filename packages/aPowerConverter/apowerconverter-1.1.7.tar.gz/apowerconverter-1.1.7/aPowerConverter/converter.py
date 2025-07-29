import sys
import re
import argparse
import os
import shutil
import subprocess
import glob
import unicodedata
from time import sleep, time
import random
import logging
from datetime import datetime

# Version information
__version__ = '1.1.3'

# Exit codes
EXIT_SUCCESS = 0      # Successful completion
EXIT_FAILURE = 1      # One or more files failed to process
EXIT_CRITICAL = 2     # Critical error (e.g., missing dependencies, invalid args)

# ANSI color codes for modern terminals
ANSI_COLORS = {
    'GREEN': '\033[92m',
    'RED': '\033[91m',
    'BLUE': '\033[94m',
    'YELLOW': '\033[93m',
    'RESET': '\033[0m',
    'BOLD': '\033[1m'
}

# Status messages and banners
CONVERSION_BANNERS = [
    "🚀 Converting documents...",
    "📚 Processing files...",
    "⚡ Starting conversion..."
]

GENERALIZE_BANNERS = [
    "\n🎩 Normalizing headings...",
    "\n🔧 Adjusting heading hierarchy...",
    "\n📏 Standardizing heading levels..."
]

CELEBRATION_MESSAGES = [
    "\n🎉 Mission accomplished!",
    "\n🌟 Conversion complete!",
    "\n✨ All done!"
]


class ColorManager:
    """Manages color output based on terminal capabilities and user preferences."""
    
    def __init__(self):
        """Initialize color manager with default settings."""
        self.force_no_color = False
    
    def set_color_mode(self, no_color: bool) -> None:
        """Set whether to force no color output."""
        self.force_no_color = no_color
    
    def should_use_color(self) -> bool:
        """Determine if color should be used based on environment and settings."""
        if self.force_no_color:
            return False
        if 'NO_COLOR' in os.environ:  # Respect NO_COLOR environment variable
            return False
        return sys.stdout.isatty()
    
    def color_text(self, text: str, color_name: str) -> str:
        """
        Safely wrap text in color codes if colors are enabled.
        
        Args:
            text: The text to colorize
            color_name: The name of the color to use
        
        Returns:
            The text wrapped in color codes if enabled, otherwise the original text
        """
        if not self.should_use_color():
            return text
        color = ANSI_COLORS.get(color_name, '')
        return f"{color}{text}{ANSI_COLORS['RESET']}"


# Global color manager instance
color_manager = ColorManager()


def get_unique_banner(banner_list: list) -> str:
    """
    Get and remove a random banner from the list.
    
    Args:
        banner_list: List of banner messages
    
    Returns:
        A random banner message, or default if list is empty
    """
    if not banner_list:
        return "🚀 Processing..."
    return banner_list.pop(random.randrange(len(banner_list)))


def setup_logging(log_file: str = None, verbose: bool = False) -> None:
    """
    Set up logging configuration.
    
    Args:
        log_file: Path to log file. If None, only console logging is set up
        verbose: If True, set logging level to DEBUG
    """
    log_level = logging.INFO
    logging.basicConfig(
        level=log_level,
        format='%(message)s',
        handlers=[logging.StreamHandler()]
    )
    
    if log_file:
        log_dir = os.path.dirname(log_file)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir)
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s [%(levelname)s] %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        ))
        logging.getLogger().addHandler(file_handler)


def check_dependencies() -> None:
    """
    Check if all required dependencies are available.
    Exits with status code 2 if critical dependencies are missing.
    """
    if shutil.which('pandoc') is None:
        logging.error("❌ Error: Pandoc is missing. Install from https://pandoc.org/installing.html")
        sys.exit(2)


def abspath_or_none(path: str) -> str:
    """
    Convert path to absolute path if it exists, otherwise return None.
    
    Args:
        path: Path to convert
    
    Returns:
        Absolute path if path exists, None otherwise
    """
    return os.path.abspath(path) if path else None


def remove_section_numbers(content: str) -> str:
    """
    Remove various section numbering styles from AsciiDoc headings.
    
    Handles:
    - Decimal: 1., 1.2., 1.2.3.
    - Roman numerals: IV., III)
    - Letters: A., B), a., b)
    - Mixed: 1a., 2b., 1.a)
    
    Args:
        content: AsciiDoc content to process
    
    Returns:
        Content with section numbers removed
    """
    pattern = (
        r'^(=+)\s+'
        r'((?:\d+[\.\)])+|(?:[IVXLCivxlc]+[\.\)])+|(?:[A-Za-z][\.\)])+|(?:\d+[A-Za-z][\.\)])+)\s+'
    )
    return '\n'.join(
        re.sub(pattern, r'\1 ', line)
        for line in content.splitlines()
    )


def format_tables(content: str) -> str:
    """
    Format tables in AsciiDoc content.
    
    Convert tables with |a| format to [INFO] blocks with ==== delimiters.
    Regular tables remain in table format.
    
    Args:
        content: AsciiDoc content to process
    
    Returns:
        Processed content with formatted tables and INFO blocks
    """
    lines = content.splitlines()
    result = []
    in_table = False
    table_lines = []
    
    i = 0
    while i < len(lines):
        line = lines[i].rstrip()
        
        # Handle table start
        if line.startswith('|==='):
            if not in_table:
                in_table = True
                table_lines = []
            else:
                # Table end
                if any('| a|' in line or '|a|' in line for line in table_lines):
                    # Convert to INFO block
                    result.append('[INFO]')
                    result.append('====')
                    
                    # Process table content
                    for tline in table_lines:
                        if '| a|' in tline:
                            content = tline.split('| a|')[1].strip()
                        elif '|a|' in tline:
                            content = tline.split('|a|')[1].strip()
                        else:
                            content = tline.strip()
                            
                        if content:
                            # Handle bullet points and sections
                            items = content.split('\n')
                            for item in items:
                                item = item.strip()
                                if item:
                                    if item.startswith('*'):
                                        # Keep bullet points as is
                                        result.append(item)
                                    elif ':' in item:
                                        # Format section headers with a blank line before
                                        result.append('')
                                        result.append(item)
                                    else:
                                        # Regular content
                                        result.append(item)
                    
                    result.append('====')
                    result.append('')
                else:
                    # Keep original table format
                    result.extend(['[width="100%",cols="50%,50%",]', ''])
                    result.append('|===')
                    result.extend(table_lines)
                    result.append('|===')
                    result.append('')
                in_table = False
                table_lines = []
        elif in_table:
            if line.strip():
                table_lines.append(line)
        else:
            # Skip duplicate table attributes
            if line.startswith('[width=') and i + 1 < len(lines) and lines[i + 1].startswith('[width='):
                i += 1
                continue
            result.append(line)
        i += 1
    
    return '\n'.join(result)


def normalize_punctuation(text: str) -> str:
    """
    Normalize punctuation while preserving letters with diacritics.
    
    Converts smart quotes, dashes, etc. to simple forms but keeps non-ASCII letters.
    
    Args:
        text: Text to normalize
    
    Returns:
        Text with normalized punctuation but preserved letters
    """
    char_map = {
        '\u2018': "'", '\u2019': "'", '\u201a': "'", '\u201b': "'",  # single quotes
        '\u201c': '"', '\u201d': '"', '\u201e': '"', '\u201f': '"',  # double quotes
        '\u2032': "'", '\u2033': '"', '\u2034': '"""',               # primes
        '\u2035': "'", '\u2036': '"', '\u2037': '"""',               # reversed primes
        '\u2013': '-', '\u2014': '-', '\u2010': '-',                 # dashes
        '\u2011': '-', '\u2212': '-',                                # hyphens
        '\u2026': '...',                                             # ellipsis
    }
    
    # First pass: replace known special characters
    for old, new in char_map.items():
        text = text.replace(old, new)
    
    # Second pass: handle remaining punctuation
    normalized = []
    for char in text:
        category = unicodedata.category(char)
        if category.startswith('P'):  # If it's punctuation
            norm_char = unicodedata.normalize('NFKD', char)
            normalized.append(norm_char if norm_char.isascii() else char)
        else:
            normalized.append(char)  # Keep non-punctuation as is
    
    return ''.join(normalized)


def generalize_headings(content: str) -> str:
    """
    Generalize AsciiDoc headings.
    
    1. Ensures all headings start at level 2 (==)
    2. Maintains proper heading hierarchy
    3. Removes section numbers
    4. Normalizes punctuation while preserving non-ASCII letters
    
    Args:
        content: The content of the AsciiDoc file
    
    Returns:
        The processed content with generalized headings
    """
    lines = content.splitlines()
    processed_lines = []
    
    # Regular expressions for heading detection and cleaning
    heading_pattern = r'^(=+)\s+(.+)$'
    number_pattern = r'''(?x)
        ^                                # Start of string
        (?:                             # Non-capturing group for alternatives
            \d+(?:\.\d+)*\s*[\.\)]\s*   # Decimal numbers: 1., 1.2., 1.2.3., 1)
            |                           # OR
            [IVXLCivxlc]+\s*[\.\)]\s*   # Roman numerals: IV., xi)
            |                           # OR
            [A-Za-z]\s*[\.\)]\s*        # Single letters: A., b)
        )
    '''
    
    # Find first heading level for adjustment
    first_heading_level = None
    level_adjustment = 0
    
    for line in lines:
        heading_match = re.match(heading_pattern, line)
        if heading_match and first_heading_level is None:
            first_heading_level = len(heading_match.group(1))
            level_adjustment = 2 - first_heading_level
            break
    
    if first_heading_level is None:
        return content
    
    # Process all lines with adjusted heading levels
    for line in lines:
        heading_match = re.match(heading_pattern, line)
        if heading_match:
            level_markers, heading_text = heading_match.groups()
            current_level = len(level_markers)
            
            new_level = max(2, current_level + level_adjustment)
            heading_text = re.sub(number_pattern, '', heading_text.strip())
            heading_text = normalize_punctuation(heading_text.strip())
            
            processed_lines.append(f"{'=' * new_level} {heading_text}")
        else:
            processed_lines.append(line)
    
    return '\n'.join(processed_lines)


def add_document_id(content: str, filename: str) -> str:
    """
    Add a document ID to the beginning of the AsciiDoc content.
    
    Args:
        content: The AsciiDoc content
        filename: The original filename
    
    Returns:
        Content with document ID added
    """
    base_name = os.path.splitext(os.path.basename(filename))[0]
    doc_id = f"[[{base_name}]]\n\n"
    return doc_id + content


def ensure_image_dir(image_dir: str = None) -> str:
    """
    Ensure the image directory exists.
    
    Args:
        image_dir: Path to image directory. If None, uses default 'images' dir
    
    Returns:
        Path to the image directory
    """
    if image_dir is None:
        image_dir = os.path.join(os.getcwd(), 'images')
    
    if not os.path.exists(image_dir):
        os.makedirs(image_dir)
        logging.info(f"Created image directory: {image_dir}")
    
    return image_dir


def convert_docx_to_adoc(input_file, output_file=None, keep_numbers=False, image_dir=None, dry_run=False, generalize=False):
    """Convert a DOCX file to AsciiDoc format."""
    if not os.path.exists(input_file):
        logging.error(f"❌ Input file not found: {input_file}")
        return False

    if not output_file:
        output_file = os.path.splitext(input_file)[0] + '.adoc'
    
    if dry_run:
        logging.info(f"Would convert {input_file} to {output_file}")
        return True

    image_dir = ensure_image_dir(image_dir)
    
    # Prepare pandoc command
    cmd = [
        'pandoc',
        '--wrap=none',
        '--columns=1000',
        '--extract-media=' + image_dir,
        '--from=docx',
        '--to=asciidoc',
        input_file,
        '-o', output_file
    ]

    try:
        subprocess.run(cmd, check=True, capture_output=True, text=True)
        
        # Post-process the file
        with open(output_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Apply transformations
        content = normalize_punctuation(content)
        content = format_tables(content)
        
        if not keep_numbers:
            content = remove_section_numbers(content)
        
        if generalize:
            content = generalize_headings(content)
        
        content = add_document_id(content, os.path.basename(input_file))
        
        # Write the processed content
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return True
    
    except subprocess.CalledProcessError as e:
        logging.error(f"❌ Pandoc conversion failed for {input_file}")
        logging.error(f"Error: {e.stderr}")
        return False
    except Exception as e:
        logging.error(f"❌ Error processing {input_file}: {str(e)}")
        return False


def process_files(input_files, output_dir=None, keep_numbers=False, image_dir=None, dry_run=False, quiet=False, generalize=False):
    """Process multiple input files."""
    if not input_files:
        logging.error("❌ No input files specified")
        return EXIT_FAILURE

    total_files = len(input_files)
    successful = 0
    failed = []
    start_time = time()

    if not quiet:
        banner = get_unique_banner(CONVERSION_BANNERS)
        logging.info(f"\n{banner}")
    
    for idx, input_file in enumerate(input_files, 1):
        if not quiet:
            progress = f"[{idx}/{total_files}]"
            file_name = os.path.basename(input_file)
            logging.info(f"{progress} Processing {file_name}...")
        
        output_file = None
        if output_dir:
            base_name = os.path.splitext(os.path.basename(input_file))[0] + '.adoc'
            output_file = os.path.join(output_dir, base_name)
        
        if convert_docx_to_adoc(
            input_file,
            output_file,
            keep_numbers=keep_numbers,
            image_dir=image_dir,
            dry_run=dry_run,
            generalize=generalize
        ):
            successful += 1
        else:
            failed.append(os.path.basename(input_file))
    
    if not quiet:
        elapsed = format_time(time() - start_time)
        success_msg = color_manager.color_text(
            f"✓ Successfully converted {successful} of {total_files} files",
            'GREEN'
        )
        logging.info(f"\n{success_msg} in {elapsed}")
        
        if failed:
            fail_msg = color_manager.color_text(
                f"✗ Failed to convert {len(failed)} files:",
                'RED'
            )
            logging.error(f"{fail_msg}\n- " + "\n- ".join(failed))
        
        if successful > 0:
            celebration = get_unique_banner(CELEBRATION_MESSAGES)
            logging.info(celebration)
    
    return EXIT_SUCCESS if not failed else EXIT_FAILURE


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description='Convert DOCX files to AsciiDoc format.',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        'input_files',
        nargs='+',
        help='One or more DOCX files to convert'
    )
    
    parser.add_argument(
        '-o', '--output-dir',
        help='Output directory for converted files'
    )
    
    parser.add_argument(
        '-i', '--image-dir',
        help='Base directory for extracted images'
    )
    
    parser.add_argument(
        '-k', '--keep-numbers',
        action='store_true',
        help='Keep section numbers from the original document'
    )
    
    parser.add_argument(
        '-d', '--dry-run',
        action='store_true',
        help='Show what would be done without making changes'
    )
    
    parser.add_argument(
        '-q', '--quiet',
        action='store_true',
        help='Suppress progress messages'
    )
    
    parser.add_argument(
        '-g', '--generalize',
        action='store_true',
        help='Generalize headings after conversion'
    )
    
    parser.add_argument(
        '-v', '--version',
        action='version',
        version=f'%(prog)s {__version__}'
    )
    
    return parser.parse_args()


def format_time(seconds):
    """Format time duration in a human-readable way."""
    if seconds < 60:
        return f"{seconds:.1f} seconds"
    minutes = int(seconds // 60)
    seconds = seconds % 60
    if minutes < 60:
        return f"{minutes}m {seconds:.1f}s"
    hours = int(minutes // 60)
    minutes = minutes % 60
    return f"{hours}h {minutes}m {seconds:.1f}s"


def main():
    """Main entry point."""
    try:
        args = parse_arguments()
        
        # Create output directory if needed
        if args.output_dir and not os.path.exists(args.output_dir):
            os.makedirs(args.output_dir)
        
        # Check dependencies
        check_dependencies()
        
        # Configure color output
        color_manager.set_color_mode(args.quiet)
        
        # Process files
        start_time = time()
        result = process_files(
            args.input_files,
            args.output_dir,
            args.keep_numbers,
            args.image_dir,
            args.dry_run,
            args.quiet,
            args.generalize
        )
        
        # Exit with appropriate code and message
        runtime = format_time(time() - start_time)
        if result == EXIT_SUCCESS:
            if not args.quiet:
                print(color_manager.color_text("\n😎 All files processed successfully!", 'GREEN'))
                print(color_manager.color_text(f"⏱️  Total runtime: {runtime}", 'BLUE'))
            return result
        else:
            if not args.quiet:
                print(color_manager.color_text("\n⚠️  Some files failed to process", 'RED'))
                print(color_manager.color_text(f"⏱️  Total runtime: {runtime}", 'BLUE'))
            return result
            
    except Exception as e:
        logging.error(f"❌ Critical error: {str(e)}")
        return EXIT_CRITICAL


if __name__ == '__main__':
    sys.exit(main()) 