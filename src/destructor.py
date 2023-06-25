import numbers
from typing import List, Set

from .dictionary_hasher import DictionaryHasher
from .constants import ROW_ID, PARENT_ID, NAME, TABLE, ROOT, DestructureType


DEPTH_ERROR = 'Max recursion depth exceeded: '

class Destructor:
    NESTED = 'NESTED'

    """Class that destructs (extracts JSON properties level by level)"""
    primitive_types: List[type] = [str, bool, numbers.Number]

    def __init__(self, d_hasher: DictionaryHasher, unique_id: str = '', keys_to_exclude: Set[str] = set()
                 , max_depth: int = 5):
        """
        Initializer
        param: d_hasher - Hashing object
        param: unique_id - Some unique id that is used in to generate the hash.
        param: keys_to_exclude - A set of dictionary keys to exclude from __table__ column.
        param: max_depth - The maximum recursion depth.
        """
        self.d_hasher: DictionaryHasher = d_hasher
        self._max_depth = max_depth
        self.__depth = 0
        self._unique_id = unique_id
        self.__hash_mode = unique_id
        self._keys_to_exclude = keys_to_exclude
        


    def destructure(self, data: DestructureType, parent_name: str = ROOT) -> List[DestructureType]:
        """
        Recursively extracts nested dictionaries from a dictionary and converts them to a list of dictionaries
        where each nested dictionary is a level and has a reference back to its parent.
        :param: data - Dictionary of DestructureType
        :param: parent_name - Used to determine nested object or root.
        :returns: List of DestructureType - dictionaries of primitive types.
        """
        result: List[DestructureType] = []
        level: DestructureType = {}

        # Note that the root ROW_ID is the hash of the dictionary.
        # Subsequent recursive calls will have either the hash of 
        # nested dictionaries/list.  Could be problematic if we just hash 
        # the primitive values since there could be none.
        if parent_name == ROOT and self.__hash_mode == Destructor.NESTED:
            id_hash = self.d_hasher.hash(data)
        else:
            id_hash = self.d_hasher.hash(data, self._unique_id)

        if self.__hash_mode == Destructor.NESTED:
            self._unique_id = id_hash # For use by recursive calls.

        self.__depth += 1
        for key, value in data.items():
            if self.__depth == self._max_depth:
                raise RecursionError(f"{DEPTH_ERROR}{self._max_depth}")
            
            # We choose to exclude keys here instead of above so the hash will contain the original data.
            if key in self._keys_to_exclude:
                continue

            if isinstance(value, dict):
                result.extend(self._process_nested_collections(id_hash, key, value))  # type: ignore

            elif isinstance(value, list):
                if all(type(v) in Destructor.primitive_types for v in value):
                    child_hash = self.d_hasher.hash(value, self._unique_id)
                    result.append({NAME: key, TABLE: value, PARENT_ID: id_hash, ROW_ID: child_hash})
                else:
                    # Mix of primitive and dict/list.
                    for v in value:
                        if type(v) in Destructor.primitive_types:
                            child_hash = self.d_hasher.hash(v, self._unique_id)
                            result.append({NAME: key, TABLE: value, PARENT_ID: id_hash, ROW_ID: child_hash})
                        else:
                            result.extend(self._process_nested_collections(id_hash, key, v))
                            #result.extend([self.destructure(val, key) for val in v])
            else:
                level[key] = value
        
        # Siblings
        level = {NAME: parent_name, TABLE: level, ROW_ID: id_hash}
        result.append(level)

        if parent_name == ROOT:
            # Root could contain immediate child hashes.
            level[NAME] = ROOT
            level[PARENT_ID] = None
            level[ROW_ID] = id_hash
            self.__depth = 0
         
        return result


    def _process_nested_collections(self, id_hash: str, key: str, value: DestructureType) -> List[DestructureType]:
        """
        Part of the recursive call to destructure if the passed in value is not all primitive types.
        :param: key - The JSON property
        :param: value - The JSON value
        :returns: DestructureType
        """
        nested_collections: List[DestructureType] = self.destructure(value, key)
        for nc in nested_collections:
            if PARENT_ID not in nc:
                nc[PARENT_ID] = id_hash # type: ignore

        return nested_collections
