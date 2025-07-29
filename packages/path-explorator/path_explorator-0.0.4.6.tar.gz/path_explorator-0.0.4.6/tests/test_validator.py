import unittest
from src.path_explorator.core import PathValidator
from pathlib import Path
from utils import get_folder_test_path

class TestValidator(unittest.TestCase):
    def setUp(self):
        self.test_folder = get_folder_test_path()
        self.validator = PathValidator()

    def test_is_goes_beyond_limits(self):
        limit_path: Path = self.test_folder
        limit_path = Path('/home/butcho/пайтон проекты/media_storage/storage')
        safe_path = Path(limit_path / Path('movies/brat.movie'))
        unsafe_path = Path(Path.cwd() / Path('__init__.py'))
        safe_path = Path('/home/butcho/пайтон проекты/media_storage/storage')
        unsafe_path = Path('/home/butcho/c_scratches/main.c')
        is_safe = not self.validator.is_goes_beyond_limits(limit_path.__str__(), safe_path.__str__())
        is_unsafe = self.validator.is_goes_beyond_limits(limit_path.__str__(), unsafe_path.__str__())
        self.assertTrue(is_safe)
        self.assertTrue(is_unsafe)


