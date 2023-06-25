from typing import Callable, Dict, List, Union
import hashlib
import json
import numbers

from src.constants import DestructureType, ExpectedTypes

JsonType = Union[str, bool, numbers.Number, List['JsonType'], 'JsonTree'] # ignore: type
JsonTree = Dict[str, JsonType]
StrTreeType = Union[str, List['StrTreeType'], 'StrTree'] # ignore: type
StrTree = Dict[str, StrTreeType]


class DictionaryHasher:
    """Class which create a hash of dictionary object."""

    def __init__(self, hasher: Callable = hashlib.md5, encoding: str='UTF-8'):
        """
        Initializer
        :param: hashing function - hashlib.md5
        :param: encoding - Supported encoding.  Used only for byte conversion. Recommend not changing from default.
        """
        self._hasher: Callable = hasher
        self._encoding: str = encoding
        # Can support other output to byte_array

    def is_json(self, data: Union[bytes, bytearray, JsonType, Dict[str, ExpectedTypes]]) -> \
        Union[bytes, bytearray, JsonType, Dict[str, ExpectedTypes]]:
        """
        Determines if the passed in string is JSON
        :param: data - The non-nested json string to be hashed.
        """
        try:
            d_json = json.loads(data) # type: ignore
        except TypeError:
            return data
        except ValueError:
            return data
        return d_json

    def __sorted_dict_str(self, data: JsonType) -> StrTreeType:
        if type(data) == dict:
            return {k: self.__sorted_dict_str(data[k]) for k in sorted(data.keys())}
            #return dict(sorted(data.items()))
        elif type(data) == list:
            return [self.__sorted_dict_str(val) for val in data]
        else:
            return str(data)

    def hash(self, data: Union[DestructureType, Dict[str, ExpectedTypes], JsonType], seed: str = '') -> str:
        """
        Returns semantically invariant and deterministic hash of passed in JsonTree.
        :param: data - JsonType - The data to be hashed.
        :param: seed - str - Some unique string to be be appended to the data prior to hashing.
        """
        if seed is None: seed = ''
        d: JsonTree = self.is_json(data) # type: ignore
        return self._hasher(bytes(repr(self.__sorted_dict_str(d)), self._encoding) + bytes(seed, self._encoding)).hexdigest()