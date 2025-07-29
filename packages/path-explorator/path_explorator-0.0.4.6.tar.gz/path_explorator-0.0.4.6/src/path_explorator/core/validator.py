from ..exceptions import EntityDoesNotExists

from pathlib import Path


class PathValidator:

    def __init__(self, root_dir):
        self.root_dir = Path(root_dir)

    def clear_path(self, path: str):
        if not isinstance(path, str):
            raise TypeError(f'path arg must be str, not {type(path)}')
        return Path(path).resolve().__str__()

    def is_goes_beyond_limits(self, requesting_path: str):
        if not isinstance(requesting_path, str):
            raise TypeError(f'requesting path arg must be str, not {type(requesting_path)}')
        requesting_path = Path(self.clear_path(requesting_path))
        if self.root_dir in requesting_path.parents or self.root_dir == requesting_path:
            return False
        return True


    def is_exists(self, path: str) -> bool:
        """
        Checks if specified path exists
        :param path: path to the entity checking
        :return: exists or not True or False
        """
        if not isinstance(path, str):
            raise TypeError(f'path arg must be str, not {type(path)}')
        entity = Path(self.root_dir, path)
        return entity.exists()


    def is_file(self, path: str) -> bool:
        """
        Checks if specified entity is FILE
        :param path: path to entity
        :return: file or not
        """
        if not isinstance(path, str):
            raise TypeError(f'path arg must be str, not {type(path)}')
        entity = Path(self.root_dir, path)
        return entity.is_file()


    def is_dir(self, path: str) -> bool:
        """
        Checks if specified entity is DIRECTORY/FOLDER
        :param path: path to entity
        :return: dir or not
        """
        if not isinstance(path, str):
            raise TypeError(f'path arg must be str, not {type(path)}')
        entity = Path(self.root_dir, path)
        return entity.is_dir()