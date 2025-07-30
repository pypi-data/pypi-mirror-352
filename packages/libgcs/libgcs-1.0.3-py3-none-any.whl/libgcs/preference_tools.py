from typing import Literal
from ._base.preference_tree import *
from ._base.exception import ArgumentException


class PreferenceTree(PreferenceTreeBase):
    @staticmethod
    def from_file(filename: str, fmt: Literal['json', 'toml'] = 'json'):
        """
        Open preferences from a file

        :param fmt: tree format: toml or json
        :param filename: Preferences file name to open from
        :return: Preference Tree Object
        """
        if fmt == 'json':
            return PreferenceTree(filename=filename, loader=PreferenceLoaderJSON)
        elif fmt == 'toml':
            return PreferenceTree(filename=filename, loader=PreferenceLoaderTOML)
        else:
            raise ArgumentException

    @staticmethod
    def from_dict(pref_dict: dict):
        """
        Open preferences from a dictionary

        :param pref_dict: Preferences dictionary
        :return: Preferences Tree Object
        """
        return PreferenceTree(pref_dict=pref_dict)


if __name__ == '__main__':
    pass
