import os
from pathlib import Path
import fnmatch
import sys
import argparse


def detect_language(filename):
    """Simple file extension to language mapping."""
    ext_map = {
        '.py': 'python',
        '.js': 'javascript',
        '.java': 'java',
        '.cpp': 'cpp',
        '.c': 'c',
        '.html': 'html',
        '.css': 'css',
        '.sql': 'sql',
        '.md': 'markdown',
        '.txt': 'text',
        '.json': 'json',
        '.yml': 'yaml',
        '.yaml': 'yaml',
        '.xml': 'xml',
        '.sh': 'bash',
        '.tpl': 'tpl',
    }
    return ext_map.get(Path(filename).suffix.lower(), 'text')


def should_skip(path, excluded_patterns, excluded_dirs, excluded_extensions):
    """
    Check if a file or directory should be skipped based on exclusion rules.

    Args:
        path: Path to check
        excluded_patterns: List of glob patterns to exclude
        excluded_dirs: List of directory names to exclude
        excluded_extensions: List of file extensions to exclude
    """
    # Convert path to Path object for easier handling
    path_obj = Path(path)

    # Check if path matches any excluded pattern
    for pattern in excluded_patterns:
        if fnmatch.fnmatch(str(path_obj), pattern):
            return True

    # Check if any parent directory should be excluded
    for parent in path_obj.parents:
        if parent.name in excluded_dirs:
            return True

    # Check file extension
    if path_obj.suffix.lower() in excluded_extensions:
        return True

    return False


def generate_claude_context(
        root_dir,
        max_file_size_mb=5,
        allowed_extensions=None,
        excluded_patterns=None,
        excluded_dirs=None,
        excluded_extensions=None
):
    """
    Generate Claude-friendly context from directory structure.

    Args:
        root_dir (str): Root directory to scan
        max_file_size_mb (float): Maximum file size in MB to process
        allowed_extensions (set): Set of allowed extensions (e.g., {'.py', '.txt'})
        excluded_patterns (list): List of glob patterns to exclude (e.g., ['*.log', '*.tmp'])
        excluded_dirs (list): List of directory names to exclude (e.g., ['node_modules', '.git'])
        excluded_extensions (list): List of file extensions to exclude (e.g., ['.pyc', '.class'])
    """
    max_file_size = max_file_size_mb * 1024 * 1024
    output = []

    # Initialize exclusion lists
    excluded_patterns = excluded_patterns or []
    excluded_dirs = excluded_dirs or []
    excluded_extensions = set(ext.lower() for ext in (excluded_extensions or []))

    # Start with project structure overview
    output.append("<project_structure>")
    for dirpath, dirnames, filenames in os.walk(root_dir):
        # Skip excluded directories
        dirnames[:] = [d for d in dirnames if d not in excluded_dirs]

        rel_path = os.path.relpath(dirpath, root_dir)

        # Skip if this directory matches exclusion patterns
        if should_skip(rel_path, excluded_patterns, excluded_dirs, excluded_extensions):
            continue

        if rel_path == '.':
            output.append(f"Root directory: {os.path.basename(os.path.abspath(root_dir))}")
        else:
            output.append(f"Directory: {rel_path}")

        for file in filenames:
            filepath = os.path.join(rel_path, file)
            if not should_skip(filepath, excluded_patterns, excluded_dirs, excluded_extensions):
                output.append(f"  - {file}")

    output.append("</project_structure>\n")

    # Process each file
    for dirpath, dirnames, filenames in os.walk(root_dir):
        # Skip excluded directories
        dirnames[:] = [d for d in dirnames if d not in excluded_dirs]

        for filename in filenames:
            filepath = os.path.join(dirpath, filename)
            relative_path = os.path.relpath(filepath, root_dir)
            file_extension = os.path.splitext(filename)[1].lower()

            # Skip if file matches exclusion criteria
            if should_skip(relative_path, excluded_patterns, excluded_dirs, excluded_extensions):
                continue

            # Skip if not in allowed extensions (if specified)
            if allowed_extensions and file_extension not in allowed_extensions:
                continue

            try:
                file_size = os.path.getsize(filepath)
                if file_size > max_file_size:
                    print(f"Skipping {filepath}: File size {file_size / 1024 / 1024:.2f}MB exceeds limit")
                    continue

                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()

                        output.append("<document>")
                        output.append(f"<source>{relative_path}</source>")

                        language = detect_language(filename)
                        if language != 'text':
                            output.append(f"<language>{language}</language>")

                        output.append(f"<file_size>{file_size}</file_size>")
                        output.append("<document_content>")
                        output.append(content.strip())
                        output.append("</document_content>")
                        output.append("</document>")
                        output.append("")

                except UnicodeDecodeError:
                    output.append("<document>")
                    output.append(f"<source>{relative_path}</source>")
                    output.append(f"<file_type>binary</file_type>")
                    output.append(f"<file_size>{file_size}</file_size>")
                    output.append("</document>")
                    output.append("")

            except Exception as e:
                print(f"Error processing {filepath}: {str(e)}")

    return "\n".join(output)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Generate Claude-friendly context from directory structure')
    parser.add_argument('directory', nargs='?', default='.', help='Directory to process')
    parser.add_argument('--max-size', type=float, default=5, help='Maximum file size in MB')
    parser.add_argument('--extensions', type=str,
                        help='Comma-separated list of allowed extensions (e.g., .py,.txt,.md)')
    parser.add_argument('--exclude-patterns', type=str, help='Comma-separated list of glob patterns to exclude')
    parser.add_argument('--exclude-dirs', type=str, help='Comma-separated list of directory names to exclude')
    parser.add_argument('--exclude-extensions', type=str, help='Comma-separated list of file extensions to exclude')

    args = parser.parse_args()

    # Process command line arguments
    allowed_extensions = set(ext.strip() for ext in args.extensions.split(',')) if args.extensions else None
    excluded_patterns = [p.strip() for p in args.exclude_patterns.split(',')] if args.exclude_patterns else []
    excluded_dirs = [d.strip() for d in args.exclude_dirs.split(',')] if args.exclude_dirs else []
    excluded_extensions = [e.strip() for e in args.exclude_extensions.split(',')] if args.exclude_extensions else []

    # Add common directories to exclude if not specifically included
    default_excludes = {'.git', '__pycache__', 'node_modules', 'venv', '.env', 'data'}
    excluded_dirs.extend(d for d in default_excludes if d not in excluded_dirs)

    context = generate_claude_context(
        args.directory,
        max_file_size_mb=args.max_size,
        allowed_extensions=allowed_extensions,
        excluded_patterns=excluded_patterns,
        excluded_dirs=excluded_dirs,
        excluded_extensions=excluded_extensions
    )

    output_file = "claude_context.txt"
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(context)

    print(f"\nContext has been saved to {output_file}")
    print(f"Total size of output file: {os.path.getsize(output_file) / 1024 / 1024:.2f}MB")
