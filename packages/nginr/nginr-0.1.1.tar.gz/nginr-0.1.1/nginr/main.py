#!/usr/bin/env python3
"""
Nginr Interpreter
"""

import sys
import os
import ast
import tokenize
import io
import re

def preprocess_source(source):
    """Preprocess source code to replace 'fn' with 'def'"""
    # Gunakan regex untuk mengganti 'fn' yang diikuti dengan nama fungsi
    # Pastikan 'fn' bukan bagian dari identifier lain
    pattern = r'\bfn\s+([a-zA-Z_][a-zA-Z0-9_]*\s*\()'
    return re.sub(pattern, r'def \1', source)

def run_file(file_path):
    """Run a .xg file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            source = f.read()
        
        # Preprocess the source
        processed_source = preprocess_source(source)
        
        # Compile and execute the code
        code = compile(processed_source, file_path, 'exec')
        exec(code, {'__name__': '__main__', '__file__': file_path})
        
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error executing {file_path}: {e}", file=sys.stderr)
        sys.exit(1)

# nginr/main.py
def main():
    import sys
    if len(sys.argv) < 2:
        print("Usage: nginr <file.xg>")
        sys.exit(1)
    
    file_path = sys.argv[1]
    if not file_path.endswith('.xg'):
        print("Error: File must have .xg extension", file=sys.stderr)
        sys.exit(1)
    
    run_file(file_path)

if __name__ == '__main__':
    main()

if __name__ == '__main__':
    main()
