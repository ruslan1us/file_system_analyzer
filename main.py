import os
import sys
import argparse

from file_system_analyzer import FileSystemAnalyzer

def main():
    # Set up command-line argument parsing
    parser = argparse.ArgumentParser(description='Analyze File System Structure')
    parser.add_argument('directory', type=str, help='Directory to analyze')
    parser.add_argument('-t', '--threshold', type=int, default=100,
                        help='Large file size threshold in MB (default: 100)')

    # Parse arguments
    args = parser.parse_args()

    # Convert threshold to bytes
    size_threshold = args.threshold * 1024 * 1024

    # Validate directory
    if not os.path.isdir(args.directory):
        print(f"Error: {args.directory} is not a valid directory")
        sys.exit(1)

    # Create and run analyzer
    analyzer = FileSystemAnalyzer(args.directory, size_threshold)
    analyzer.traverse_directory()
    analyzer.generate_report()


if __name__ == '__main__':
    main()