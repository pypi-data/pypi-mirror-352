import os

from abc import ABC, abstractmethod
from os import PathLike
from pathlib import Path
from typing import IO, AnyStr, Union


class FileUtil:
    @staticmethod
    def new_filename(filename: str) -> str:
        path = Path(filename)
        stem = path.stem
        suffix = path.suffix
        parent = path.parent

        idx = 0
        while True:
            candidate = parent / f"{stem}_{idx}{suffix}"
            if not candidate.exists():
                return str(candidate)
            idx += 1

    @staticmethod
    def mkdir(dirname: str):
        """
        Make a new directory

        :param dirname: Directory name
        :return:
        """
        if dirname:
            os.makedirs(dirname, exist_ok=True)

    @staticmethod
    def exists(path: str | Path) -> bool:
        return Path(path).exists()

    @staticmethod
    def insert_at_line(filename: str, line_no: int, text: str, latest_pos: int = 0):
        """
        This static method inserts a line into mth line (m >= 0) which
        is an optimized alternative of rewriting the whole file.

        :param filename: File name or file path (str)
        :param line_no: Line number, can be absolute (>= 0) or relative to last element (< 0)
        :param text: Object which str() is callable to insert
        :param latest_pos: The latest file pointer position, put the return value of last position
        :return: The latest file position, put it in next argument call
        """
        last_end = []
        _p_file = 0
        with open(filename, "r+", encoding='utf-8') as fro:
            if latest_pos == 0:
                if line_no < 0:
                    _max_line = FileUtil.line_count(fro)
                    _lineno = _max_line + line_no
                else:
                    _lineno = line_no
                fro.seek(0)
                if _lineno < 0:
                    _lineno = 0
                _pos = 0
                _line = fro.readline()
                while _line:
                    if _pos == _lineno - 1:
                        _p_file = fro.tell()
                    if _pos >= _lineno:
                        last_end.append(_line)
                    _line = fro.readline()
                    _pos += 1
                fro.seek(_p_file)
            else:
                fro.seek(latest_pos)
                _line = fro.readline()
                while _line:
                    last_end.append(_line)
                    _line = fro.readline()
                fro.seek(latest_pos)
            fro.write(str(text) + '\n')
            new_latest_pos = fro.tell()
            fro.writelines(last_end)
        return new_latest_pos

    @staticmethod
    def blocks(file_object: IO, size: int = 2 ** 16):
        """
        Lazy block read

        :param file_object: File object
        :param size: Block size
        :return:
        """
        while True:
            b = file_object.read(size)
            if not b:
                break
            yield b


class File(ABC):
    """
    Provides an abstraction for file handling operations.

    This class encapsulates common file operations such as reading, writing,
    appending, and file metadata management. The purpose of this class is to
    facilitate file manipulations while ensuring directory existence and proper
    handling of file paths. It simplifies usage of file-related operations for
    users through a consistent interface.

    The expected usage involves initializing a file object with a given file path
    and performing required operations such as reading its content, writing to it,
    or checking its existence. The class ensures seamless directory creation
    when trying to access or write to a file path for the first time.
    """

    def __init__(self, path: Union[str, PathLike[AnyStr]], *, unique: bool = False):
        self._path = FileUtil.new_filename(path) if unique else path
        if not FileUtil.exists(self._path):
            FileUtil.mkdir(os.path.dirname(self._path))
            self.touch()

    def read(self) -> str:
        """
        Reads the contents of a file from the specified path provided during initialization. This
        method opens the file in read mode with UTF-8 encoding and returns its entire content
        as a string.

        :return: The contents of the file as a string.
        """
        with open(self._path, 'r', encoding='utf-8') as f:
            return f.read()

    def readlines(self, strip_newlines: bool = True) -> list[str]:
        """
        Reads all lines from a file specified by the instance's `_path` attribute.

        This method opens the file in read mode with UTF-8 encoding and processes its content.
        It can optionally strip trailing newline characters (`\r\n`) from each line.

        :param strip_newlines: If True, removes trailing newline characters from each line. Default is True.
        :return: A list of strings representing lines in the file. Each string is stripped of
                 newline characters if `strip_newlines` is True.
        """
        with open(self._path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        return [line.rstrip('\r\n') for line in lines] if strip_newlines else lines

    def write(self, content: AnyStr) -> None:
        """
        Writes the provided content to the specified file in write mode. This method
        opens the file at the path `_path` stored within the instance and writes the
        given `content` to it. The file will be encoded in UTF-8. If the file
        already exists, it will be overwritten.

        :param content: The content to write into the file.

        :return: None
        """
        with open(self._path, 'w', encoding='utf-8') as f:
            f.write(content)

    def append(self, content) -> None:
        """
        Appends the provided content to the file associated with the instance. This method
        opens the file in append mode and writes the given content at the end of the file.

        :param content: The text content to be appended to the file.
        :type content: str
        :return: None
        """
        with open(self._path, 'a', encoding='utf-8') as f:
            f.write(content)

    def append_line(self, line: Union[str, AnyStr]) -> None:
        """
        Appends a single line of text to the file associated with the instance.

        This method opens the file in append mode and writes the given line,
        including a newline character, to the file. The file is encoded in UTF-8
        to ensure compatibility with a wide range of text content.

        :param line: The line of text to append to the file. Must be a string.
        :return: None
        """
        with open(self._path, 'a', encoding='utf-8') as f:
            f.write(f'{line}\n')

    def exists(self) -> bool:
        """
        Determines if the specified path exists on the file system.

        This method checks whether the path provided to the instance of the class
        exists in the file system. It acts as a wrapper around the `os.path.exists`
        function to perform the existence check.

        :return: True if the path exists, False otherwise
        """
        return os.path.exists(self._path)

    def size(self) -> int:
        """
        Determine the size of the file at the given path.

        This method calculates the size of the file specified by the current object's
        path attribute if the file exists. If the file does not exist, it returns 0.

        :return: The size of the file in bytes if it exists, otherwise 0
        """
        return os.path.getsize(self._path) if self.exists() else 0

    def delete(self) -> None:
        """
        Deletes a file if it exists. This method checks the existence of the file
        associated with the given path and removes it from the filesystem if found.

        :return: None
        """
        if self.exists():
            os.remove(self._path)

    def touch(self) -> None:
        """
        Creates a new file if it does not exist using the specified path.

        The `touch` method ensures the existence of a file at the location
        indicated by `self._path`. If the file does not exist, an empty file
        is created. If the file already exists, its modification time is
        updated without altering its content.

        :return: None
        """
        open(self._path, 'a').close()

    def clear(self) -> None:
        """
        Clears the content by writing an empty string.

        This method effectively removes any content by overwriting it with
        an empty string. It is intended for scenarios where the existing
        data needs to be cleared.

        :return: None
        """
        self.write('')

    def lc(self) -> int:
        """
        Calculates the total number of lines in a file.

        This method reads the file specified by the `_path` attribute line by line
        and counts the total number of lines present in the file. The method ensures
        the file is opened using UTF-8 encoding for proper handling of text content.

        :return: The total number of lines in the file.
        """
        with open(self._path, 'r', encoding='utf-8') as fro:
            return sum(1 for _ in fro)  # line count

    def wc(self) -> int:
        """
        Counts the total number of words in the file specified by the `path` attribute.

        The method opens the file in read mode using UTF-8 encoding and iterates through
        each line and each character in the file. It identifies word boundaries by checking
        whitespace characters. The count increments when encountering the start of a new
        word. This method ensures efficient traversal of the file, especially for large
        text files.

        :return: Total number of words in the file.
        """
        count = 0
        in_word = False
        with open(self.path, 'r', encoding='utf-8') as f:
            for line in f:
                for char in line:
                    if char.isspace():
                        in_word = False
                    elif not in_word:
                        count += 1
                        in_word = True
        return count  # word count

    @property
    def path(self) -> Union[str, PathLike[AnyStr]]:
        return self._path


if __name__ == '__main__':
    f1 = File('hello.txt')
    print(f1.wc())
