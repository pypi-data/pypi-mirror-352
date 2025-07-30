from pprint import pprint
from typing import Type
from .exception import ArgumentException
from .preference_loader import PreferenceLoaderBase, PreferenceLoaderJSON, PreferenceLoaderTOML


class PreferenceTreeBase:
    def __init__(self, filename: str = None,
                 pref_dict: dict = None,
                 loader: Type[PreferenceLoaderBase] = PreferenceLoaderJSON,
                 default_filename='settings.json'):
        self.__loader = loader
        self.__pref: dict | None = None
        self.__filename = default_filename

        if filename is not None and pref_dict is not None:
            raise ArgumentException(f'Wrong argument called on {self.__class__.__name__}!')
        if filename is None and pref_dict is None:
            raise ArgumentException(f'No argument called on {self.__class__.__name__}!')
        if filename is not None:
            self.__filename = filename
            self.__pref = self.__loader.load(filename)
        elif pref_dict is not None:
            self.__pref = pref_dict

    @property
    def tree(self) -> dict:
        return self.__pref

    def to_dict(self):
        return self.tree

    def __getitem__(self, item: str):
        return self.__pref.__getitem__(item)

    def __setitem__(self, key, value):
        self.__pref.__setitem__(key, value)

    def __contains__(self, item):
        return self.__pref.__contains__(item)

    def setdefault(self, key, value):
        self.__pref.setdefault(key, value)

    def remove(self, key):
        """
        Remove value from the preference tree

        :param key: Key
        :return: Value removed
        """
        return self.__pref.pop(key)

    def __len__(self):
        return self.__pref.__len__()

    def save(self, filename: str = None,
             fallback_loader: Type[PreferenceLoaderBase] = PreferenceLoaderJSON):
        """
        Save the preference tree to a file if possible

        :param filename: File name to save to
        :param fallback_loader: Fallback Loader
        :return:
        """

        def _wr(_loader: Type[PreferenceLoaderBase]):
            if filename is None:
                _loader.write(self.__pref, self.__filename)
            else:
                _loader.write(self.__pref, filename)

        try:
            _wr(self.__loader)
        except TypeError:
            _wr(fallback_loader)

    def print(self):
        pprint(self.__pref)

    def __str__(self):
        return str(self.__pref)

    def __repr__(self):
        return self.__str__()
