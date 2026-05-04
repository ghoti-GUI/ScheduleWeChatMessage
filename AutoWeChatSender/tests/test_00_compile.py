import py_compile
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]


class TestCompile(unittest.TestCase):
    def test_compile_all_python_files(self):
        exclude_dirs = {
            "__pycache__",
            "build",
            "dist",
            ".git",
            ".venv",
            "venv",
        }

        py_files = [
            path for path in PROJECT_ROOT.rglob("*.py")
            if not any(part in exclude_dirs for part in path.parts)
        ]

        self.assertGreater(len(py_files), 0, "没有找到 Python 文件")

        for py_file in py_files:
            with self.subTest(file=str(py_file)):
                py_compile.compile(str(py_file), doraise=True)


if __name__ == "__main__":
    unittest.main()