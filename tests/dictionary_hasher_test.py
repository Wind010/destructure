import hashlib
import pytest
from assertpy import assert_that
from unittest.mock import MagicMock
from src.dictionary_hasher import DictionaryHasher


class TestDictionaryHasher(): 

    def test__init__valid_values_initialized(self):
        d_hasher = DictionaryHasher()
        
        assert_that(d_hasher).is_not_none()
        assert_that(d_hasher._hasher).is_equal_to(hashlib.md5)
        assert_that(d_hasher._encoding).is_equal_to('UTF-8')


    def test_init__sha1_ascii__initialized(self):
        d_hasher = DictionaryHasher(hashlib.sha1, 'ascii')
        
        assert_that(d_hasher).is_not_none()
        assert_that(d_hasher._hasher).is_equal_to(hashlib.sha1)
        assert_that(d_hasher._encoding).is_equal_to('ascii')
        
    
    @pytest.mark.parametrize("input", [('i_am_not_json'), (''), (None), ('{"property": malformed}')],
                            ids=['not_json', 'empty_string', 'none', 'invalid_json'])
    def test_is_json__is_not_json__returns_json_tree(self, input):
        d_hasher = DictionaryHasher()
        output = d_hasher.is_json(input)
        assert_that(output).is_equal_to(input)


    @pytest.mark.parametrize("input, expected_output"
                                    , [('{"property": 1}', {'property': 1})
                                    , ('{"property": "string"}', {'property': 'string'})
                                    , ('{"property": []}', {'property': []})
                                    , ('{"property": {}}', {'property': {}}) ],
                            ids=['integer', 'string', 'array', 'nested'])
    def test_is_json__valid_json__returns_json_tree(self, input, expected_output):
        d_hasher = DictionaryHasher()
        output = d_hasher.is_json(input)
        assert_that(output).is_instance_of(dict)
        assert_that(output).is_equal_to(expected_output)


    def test_is_json__dict__returns_json_tree(self):
        d_hasher = DictionaryHasher()
        input = {'a': 1}
        output = d_hasher.is_json(input)
        assert_that(output).is_instance_of(dict)
        assert_that(output).is_equal_to(input)


    def test_hash__empty_seed__returns_hash(self):
        d_hasher = DictionaryHasher()
        hash = d_hasher.hash('{"property": 1}')
        assert_that(hash).is_equal_to('2e7f878d2fe542b7ef62894919d461d8')

    def test_hash__seed_is_none__returns_hash(self):
        d_hasher = DictionaryHasher()
        hash = d_hasher.hash('{"property": 1}', None)
        assert_that(hash).is_equal_to('2e7f878d2fe542b7ef62894919d461d8')

    def test_hash__seed_specified__returns_hash(self):
        d_hasher = DictionaryHasher()
        hash = d_hasher.hash('{"property": 1}', '🖖')
        assert_that(hash).is_equal_to('183d390ecb907dc0ad00bcf1c6b53b75')