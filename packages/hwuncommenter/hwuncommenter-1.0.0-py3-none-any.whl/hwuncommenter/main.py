#!/usr/bin/env python3
"""
HwUncommenter - Universal Comment Remover
Removes comments from source code files in any programming language
"""

import re
import sys
import argparse
from pathlib import Path


class HwUncommenter:
    def __init__(self):
        # Define comment patterns for different languages
        self.comment_patterns = {
            # Single line comments
            'single_line': [
                r'//.*$',           # C, C++, Java, JavaScript, etc.
                r'#.*$',            # Python, Ruby, Perl, Shell, etc.
                r'--.*$',           # SQL, Lua, Haskell
                r';.*$',            # Assembly, Lisp, Clojure
                r'%.*$',            # Prolog, Erlang
                r"'.*$",            # VB.NET (single quote comments)
                r'!.*$',            # Fortran
                r'REM\s+.*$',       # Batch files
                r'@rem\s+.*$',      # Batch files (alternative)
            ],
            
            # Multi-line comments
            'multi_line': [
                (r'/\*', r'\*/'),   # C, C++, Java, JavaScript, CSS
                (r'<!--', r'-->'),  # HTML, XML
                (r'\(\*', r'\*\)'), # Pascal, Modula
                (r'\{-', r'-\}'),   # Haskell
                (r'"""', r'"""'),   # Python docstrings
                (r"'''", r"'''"),   # Python docstrings
            ]
        }

    def remove_comments_from_content(self, content):
        """Remove all comments from the given content"""
        lines = content.split('\n')
        cleaned_lines = []
        in_multiline_comment = False
        multiline_end_pattern = None
        
        for line in lines:
            original_line = line
            
            # Handle multi-line comments
            if in_multiline_comment:
                # Look for end of multi-line comment
                if multiline_end_pattern and re.search(multiline_end_pattern, line):
                    # Remove everything up to and including the end pattern
                    line = re.sub(f'.*?{multiline_end_pattern}', '', line)
                    in_multiline_comment = False
                    multiline_end_pattern = None
                else:
                    # Entire line is part of multi-line comment
                    continue
            
            # Check for start of multi-line comments
            for start_pattern, end_pattern in self.comment_patterns['multi_line']:
                if re.search(start_pattern, line):
                    # Check if comment ends on same line
                    if re.search(end_pattern, line):
                        # Remove the entire comment block on same line
                        line = re.sub(f'{start_pattern}.*?{end_pattern}', '', line)
                    else:
                        # Multi-line comment starts here
                        line = re.sub(f'{start_pattern}.*$', '', line)
                        in_multiline_comment = True
                        multiline_end_pattern = end_pattern
                        break
            
            # Remove single-line comments (only if not in multi-line comment)
            if not in_multiline_comment:
                for pattern in self.comment_patterns['single_line']:
                    # Handle string literals - don't remove comments inside strings
                    # This is a simplified approach; more complex parsing would be needed for perfect accuracy
                    if not self._is_in_string_literal(line, pattern):
                        line = re.sub(pattern, '', line, flags=re.IGNORECASE)
            
            # Only add line if it's not empty or contains non-whitespace
            if line.strip() or not original_line.strip():
                cleaned_lines.append(line.rstrip())
        
        return '\n'.join(cleaned_lines)

    def _is_in_string_literal(self, line, comment_pattern):
        """Basic check to avoid removing comments inside string literals"""
        # This is a simplified implementation
        # Find the position where comment would be removed
        match = re.search(comment_pattern, line)
        if not match:
            return False
        
        comment_pos = match.start()
        
        # Count quotes before comment position
        single_quotes = line[:comment_pos].count("'") - line[:comment_pos].count("\\'")
        double_quotes = line[:comment_pos].count('"') - line[:comment_pos].count('\\"')
        
        # If odd number of quotes, we're likely inside a string
        return (single_quotes % 2 == 1) or (double_quotes % 2 == 1)

    def process_file(self, filepath):
        """Process a single file and remove comments"""
        try:
            file_path = Path(filepath)
            if not file_path.exists():
                print(f"Error: File '{filepath}' not found.")
                return False
            
            # Read file content
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # Remove comments
            cleaned_content = self.remove_comments_from_content(content)
            
            # Write back to file
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(cleaned_content)
            
            print(f"Successfully removed comments from '{filepath}'")
            return True
            
        except Exception as e:
            print(f"Error processing file '{filepath}': {str(e)}")
            return False


def main():
    parser = argparse.ArgumentParser(
        description='HwUncommenter - Universal Comment Remover\nRemoves ALL comment lines from source code files in any programming language.',
        epilog='HwUncommenter by MalikHw47\nSupports: C/C++, Java, Python, JavaScript, HTML, CSS, SQL, Shell, and many more!',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        'file',
        help='Path to the source code file to process'
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version='HwUncommenter 1.0.0 by MalikHw47'
    )
    
    if len(sys.argv) == 1:
        parser.print_help()
        return
    
    args = parser.parse_args()
    
    # Create uncommenter instance and process file
    uncommenter = HwUncommenter()
    success = uncommenter.process_file(args.file)
    
    if not success:
        sys.exit(1)


if __name__ == '__main__':
    main()
