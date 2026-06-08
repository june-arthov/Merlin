import unittest
import os
import sys
# Add parent dir to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from merlin.tools.base import ToolRegistry
from merlin.tools.system import RunShellCommand, WriteFile
from merlin.tools.file_ops import ReadFile, ListDirectory, Replace

class TestMerlinTools(unittest.TestCase):
    def setUp(self):
        self.registry = ToolRegistry()
        self.test_file = "tests/test_file.txt"
        if os.path.exists(self.test_file):
            os.remove(self.test_file)

    def test_registry(self):
        self.registry.register(RunShellCommand())
        self.assertIn("run_shell_command", self.registry.tools)

    def test_write_and_read(self):
        write_tool = WriteFile()
        write_tool.execute(self.test_file, "Hello Merlin")
        
        read_tool = ReadFile()
        result = read_tool.execute(self.test_file)
        self.assertEqual(result["content"], "Hello Merlin")

    def test_replace(self):
        write_tool = WriteFile()
        write_tool.execute(self.test_file, "Hello World")
        
        replace_tool = Replace()
        replace_tool.execute(self.test_file, "World", "Merlin")
        
        read_tool = ReadFile()
        result = read_tool.execute(self.test_file)
        self.assertEqual(result["content"], "Hello Merlin")

    def tearDown(self):
        if os.path.exists(self.test_file):
            os.remove(self.test_file)

if __name__ == "__main__":
    unittest.main()
