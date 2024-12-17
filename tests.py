import os
import shutil
import tempfile
import unittest
from PIL import Image
from file_system_analyzer import FileSystemAnalyzer



class TestFileSystemAnalyzer(unittest.TestCase):
    def setUp(self):
        """
        Creating temp directory
        """
        self.test_dir = tempfile.mkdtemp()

        # Create some test files
        self.create_test_files()

    def tearDown(self):
        """
        Delete temp directory after every test
        """
        shutil.rmtree(self.test_dir)

    def create_test_files(self):
        """
        Create different test files
        """
        # Text
        with open(os.path.join(self.test_dir, 'text1.txt'), 'w') as f:
            f.write('This is test text file.')

        # Large file
        with open(os.path.join(self.test_dir, 'large_file.bin'), 'wb') as f:
            f.write(b'\x00' * (150 * 1024 * 1024))  # 150 MB

        img = Image.new('RGB', (10, 10), color='white')  # Not empty image
        img.save(os.path.join(self.test_dir, 'image.png'))

        # World-writable file
        writable_file = os.path.join(self.test_dir, 'writable_file.txt')
        with open(writable_file, 'w') as f:
            f.write('This is world-writable file.')
        os.chmod(writable_file, 0o666)

    def test_traverse_directory(self):
        """
        Testing traverse
        """
        analyzer = FileSystemAnalyzer(self.test_dir)
        analyzer.traverse_directory()

        # Check if files were find
        self.assertIn('Text', analyzer.file_types)
        self.assertIn('Image', analyzer.file_types)

    def test_categorize_file_type(self):
        """
        Testing for right file categorization
        """
        analyzer = FileSystemAnalyzer(self.test_dir)

        text_file = os.path.join(self.test_dir, 'text1.txt')
        image_file = os.path.join(self.test_dir, 'image.png')

        # Check classification for files
        self.assertEqual(analyzer.categorize_file_type(text_file), 'Text')
        self.assertEqual(analyzer.categorize_file_type(image_file), 'Image')  # Должно пройти

    def test_large_file_detection(self):
        """
        Testing large files
        """
        analyzer = FileSystemAnalyzer(self.test_dir, size_threshold=100 * 1024 * 1024)  # 100 MB
        analyzer.traverse_directory()

        # Checking if large file were find
        self.assertEqual(len(analyzer.large_files), 1)
        large_file = analyzer.large_files[0]
        self.assertTrue(large_file[0].endswith('large_file.bin'))
        self.assertGreater(large_file[1], 100 * 1024 * 1024)

    def test_unusual_permissions(self):
        """
        Testing if world-writable files were find
        """
        analyzer = FileSystemAnalyzer(self.test_dir)
        analyzer.traverse_directory()

        # Check if file was find
        self.assertEqual(len(analyzer.unusual_permissions), 1)
        self.assertTrue(analyzer.unusual_permissions[0].endswith('writable_file.txt'))

    def test_generate_report(self):
        """
        Testing report generation
        """
        analyzer = FileSystemAnalyzer(self.test_dir)
        analyzer.traverse_directory()

        # Checking that report don't get us an exception
        try:
            analyzer.generate_report()
        except Exception as e:
            self.fail(f"generate_report() create exception: {e}")

    def test_error_handling(self):
        """
        Testing error handling for some directories
        """
        inaccessible_dir = os.path.join(self.test_dir, 'no_access')
        os.mkdir(inaccessible_dir)
        os.chmod(inaccessible_dir, 0o000)  # Clearing access right

        analyzer = FileSystemAnalyzer(inaccessible_dir)
        try:
            analyzer.traverse_directory()
        except Exception:
            self.fail("traverse_directory() should not throw exceptions when the directory is inaccessible.")

        # Restoring access rights so tearDown can delete the directory
        os.chmod(inaccessible_dir, 0o755)


if __name__ == '__main__':
    unittest.main()
