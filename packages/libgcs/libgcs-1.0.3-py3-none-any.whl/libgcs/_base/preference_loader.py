import sys
from abc import ABC, abstractmethod

# IMPORT TOML
if sys.version_info < (3, 11):
    import tomli as toml
else:
    import tomllib as toml

# IMPORT JSON
import json


class PreferenceLoaderBase(ABC):
    @staticmethod
    @abstractmethod
    def load(filename: str):
        pass

    @staticmethod
    def write(pref_to_write: dict, inp_file_dir: str):
        pass


class PreferenceLoaderJSON(PreferenceLoaderBase):
    @staticmethod
    def load(filename: str):
        with open(filename, mode='r', encoding='utf-8') as __f:
            return json.load(__f)

    @staticmethod
    def write(pref_to_write: dict, inp_file_dir: str):
        if pref_to_write:
            with open(inp_file_dir, mode='w', encoding='utf-8') as __f:
                json.dump(pref_to_write, __f, indent=4)
            return True
        return False


class PreferenceLoaderTOML(PreferenceLoaderBase):
    @staticmethod
    def load(filename: str):
        with open(filename, mode='rb') as __f:
            return toml.load(__f)
