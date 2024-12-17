import os
import magic
import stat
from collections import defaultdict


class FileSystemAnalyzer:
    def __init__(self, directory: str, size_threshold: int = 100 * 1024 * 1024):
        """
        Initialize the File System Analyzer

        :param directory: directory to analyze
        :param size_threshold: minimum file size to be considered large (default: 100 MB)
        """
        self.directory = os.path.abspath(directory)         # normalized absolutized version of the pathname path
        self.size_threshold = size_threshold
        self.file_type_magic = magic.Magic(mime=True)

        # Data storage for analysis results
        self.file_types = defaultdict(list)
        self.file_sizes = defaultdict(int)
        self.large_files = []
        self.unusual_permissions = []

    def categorize_file_type(self, file_path: str) -> str:
        """
        Categorize file type using libmagic

        :param file_path: Path to the file
        :return: Categorized file type
        """
        try:
            # Getting mime type
            mime_type = self.file_type_magic.from_file(file_path)

            # Mapping mime types to categories
            categories = {
                'text': 'Text',
                'image': 'Image',
                'exec': 'Executable',
                'video': 'Video',
                'audio': 'Audio',
                'application/pdf': 'PDF'
            }

            if not mime_type:
                return 'Unknown'

            # Check each key in mime_type
            for key, category in categories.items():
                if key in mime_type:
                    return category
                # Extra check for '.txt' files, because when text file is empty, mimi type return different type than text
                elif os.path.splitext(file_path)[1] == '.txt':
                    return 'Text'

            # Default category
            return 'Other'
        except Exception:
            return 'Unknown'

    @staticmethod
    def analyze_permissions(file_path: str) -> bool:
        """
        Check for unusual file permissions

        :param file_path: Path to the file
        :return: True if permissions are unusual, False otherwise
        """
        try:
            file_stat = os.stat(file_path)
            mode = file_stat.st_mode

            # Check for world-writable files
            if mode & stat.S_IWOTH:
                return True

            return False
        except Exception:
            return False

    def traverse_directory(self):
        """
        Recursively traverse the directory and analyze files
        """
        try:
            for root, dirs, files in os.walk(self.directory):
                for file in files:
                    full_path = os.path.join(root, file)

                    # Skip symlinks to prevent infinite loops
                    if os.path.islink(full_path):
                        continue

                    try:
                        file_size = os.path.getsize(full_path)
                        file_type = self.categorize_file_type(full_path)

                        # Store file type information
                        self.file_types[file_type].append(full_path)
                        self.file_sizes[file_type] += file_size

                        # Check for large files
                        if file_size > self.size_threshold:
                            self.large_files.append((full_path, file_size))

                        # Check for unusual permissions
                        if self.analyze_permissions(full_path):
                            self.unusual_permissions.append(full_path)

                    except (PermissionError, OSError):
                        # Skip files we can't access
                        continue

        except PermissionError:
            print(f"Error: No permission to access directory {self.directory}")
        except Exception as e:
            print(f"Unexpected error during directory traversal: {e}")

    def generate_report(self):
        """
        Generate a comprehensive report of the file system analysis
        """
        print("\n=== File System Analysis Report ===")
        print(f"Directory Analyzed: {self.directory}\n")

        # File Type Distribution
        print("File Type Distribution:")
        for file_type, files in self.file_types.items():
            print(f"{file_type}: {len(files)} files, Total Size: {self.file_sizes[file_type] / (1024 * 1024):.4f} MB")

        # Large Files
        print("\nLarge Files (> {} MB):".format(self.size_threshold / (1024 * 1024)))
        for file, size in sorted(self.large_files, key=lambda x: x[1], reverse=True):
            print(f"{file}: {size / (1024 * 1024):.2f} MB")

        # Unusual Permissions
        print("\nFiles with Unusual Permissions:")
        for file in self.unusual_permissions:
            print(file)