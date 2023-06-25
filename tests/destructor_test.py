import unittest
from assertpy import assert_that

import json
import pytest
 
from src.constants import PARENT_ID, NAME, TABLE, ROOT, ROW_ID
from src.dictionary_hasher import DictionaryHasher

from src.destructor import Destructor, DEPTH_ERROR


class TestDestructor():

    @pytest.fixture
    def d_hasher(self) -> DictionaryHasher:
        return DictionaryHasher()
    
    def test__init__default_max_depth_and_unique_id_and_keys_to_exclude___initialized(self):
        d_hasher = DictionaryHasher()
        destructor = Destructor(d_hasher)
        assert_that(destructor).is_not_none()
        assert_that(destructor._unique_id).is_equal_to('')
        assert_that(destructor._keys_to_exclude).is_equal_to({})
        assert_that(destructor._max_depth).is_equal_to(5)


    def test__init__unique_id_and_keys_to_exclude_and_max_depth___initialized(self):
        d_hasher = DictionaryHasher()
        expected_unique_id, expected_keys_to_exclude, expected_max_depth = 'i_am_unique', {1}, 3
        destructor = Destructor(d_hasher, expected_unique_id, expected_keys_to_exclude
                                , expected_max_depth)
        assert_that(destructor).is_not_none()
        assert_that(destructor._unique_id).is_equal_to(expected_unique_id)
        assert_that(destructor._keys_to_exclude).is_equal_to(expected_keys_to_exclude)
        assert_that(destructor._max_depth).is_equal_to(expected_max_depth)


    def test__destructure__empty_dict__destructured(self, d_hasher: DictionaryHasher):
        destructor = Destructor(d_hasher)
        data = {} 

        result = destructor.destructure(data)[0]

        assert_that(result[NAME]).is_equal_to(ROOT)
        assert_that(result[TABLE]).is_equal_to(data)
        assert_that(result[ROW_ID]).is_equal_to(d_hasher.hash(data))
        assert_that(result[PARENT_ID]).is_none()

    
    def test__destructure__non_nested_dict__destructured(self, d_hasher: DictionaryHasher):
        destructor = Destructor(d_hasher)
        data = {"a": 1, "b": 2, "c": 3}

        result = destructor.destructure(data)[0]

        assert_that(result[NAME]).is_equal_to(ROOT)
        assert_that(result[TABLE]).is_equal_to(data)
        assert_that(result[ROW_ID]).is_equal_to(d_hasher.hash(data))
        assert_that(result[PARENT_ID]).is_none()


    def test__destructure__nested_and_keys_excluded__destructured(self, d_hasher: DictionaryHasher):
        destructor = Destructor(d_hasher, '', {"a"})
        data = {"a": 1, "b": 2, "c": {"a": 10}}

        result = destructor.destructure(data)

        row1, row2 = result[0], result[1]
        root_hash = d_hasher.hash(data)
        assert_that(row1[NAME]).is_equal_to("c")
        assert_that(row1[TABLE]).is_equal_to({})
        assert_that(row1[ROW_ID]).is_equal_to(d_hasher.hash({"a": 10}))
        assert_that(row1[PARENT_ID]).is_equal_to(root_hash)

        assert_that(row2[NAME]).is_equal_to(ROOT)
        assert_that(row2[TABLE]).is_equal_to({"b": 2})
        assert_that(row2[ROW_ID]).is_equal_to(root_hash)
        assert_that(row2[PARENT_ID]).is_none()


    def test__destructure__maximum_depth__destructured(self, d_hasher: DictionaryHasher):
        expected_depth = 2
        destructor = Destructor(d_hasher, "", {}, expected_depth)
        data = {"a": 1, "b": 2, "c": {"x": 9, "y": {"z": 8}}}

        with pytest.raises(RecursionError) as ex:
            destructor.destructure(data)
        
        assert_that(str(ex.value)).is_equal_to(f"{DEPTH_ERROR}{expected_depth}")


    def test__destructure__hash_mode_nested_and_two_levels__destructured(self, d_hasher: DictionaryHasher):
        destructor = Destructor(d_hasher, Destructor.NESTED)
        data = {"a": 1, "b": 2, "c": {"x": 9}}
        target_key = 'c'
        result = destructor.destructure(data)

        row1, row2 = result[0], result[1]
        level_2_value = {k: v for k, v in data[target_key].items()}
        level_1_value = {k: v for k, v in data.items() if k != target_key}
        assert_that(row1[NAME]).is_equal_to(target_key)
        assert_that(row1[TABLE]).is_equal_to(level_2_value)
        assert_that(row1[ROW_ID]).is_equal_to(d_hasher.hash(level_2_value, d_hasher.hash(data)))
        assert_that(row1[PARENT_ID]).is_equal_to(row2[ROW_ID])

        assert_that(row2[NAME]).is_equal_to(ROOT)
        assert_that(row2[TABLE]).is_equal_to(level_1_value)
        assert_that(row2[ROW_ID]).is_equal_to(d_hasher.hash(data))
        assert_that(row2[PARENT_ID]).is_none()


    def test__destructure__hash_mode_nested_and_three_levels_destructured(self, d_hasher: DictionaryHasher):
        destructor = Destructor(d_hasher, Destructor.NESTED)
        data = {"a": 1, "b": 2, "c": {"x": 9, "y": {"z": 8}}}
        target_key_1, target_key_2 = 'c', 'y'
        result = destructor.destructure(data)
        
        row1, row2, row3 = result[0], result[1], result[2]
        level_1_value = {k: v for k, v in data.items() if k != target_key_1}
        level_1_hash = d_hasher.hash(data)
        level_2_data = {k: v for k, v in data.items() if k == target_key_1}[target_key_1]
        level_2_value = {k: v for k, v in data[target_key_1].items() if k != target_key_2}
        level_2_hash = d_hasher.hash(level_2_data, d_hasher.hash(data))
        level_3_data = {k:v for k, v in data[target_key_1].items() if k == target_key_2}
        level_3_value = level_3_data[target_key_2]
        level_3_hash = d_hasher.hash(level_3_value, level_2_hash)
        assert_that(row1[NAME]).is_equal_to(target_key_2)
        assert_that(row1[TABLE]).is_equal_to(level_3_value)
        assert_that(row1[ROW_ID]).is_equal_to(level_3_hash)
        assert_that(row1[PARENT_ID]).is_equal_to(row2[ROW_ID])
        assert_that(row1[PARENT_ID]).is_equal_to(level_2_hash)

        assert_that(row2[NAME]).is_equal_to(target_key_1)
        assert_that(row2[TABLE]).is_equal_to(level_2_value)
        assert_that(row2[ROW_ID]).is_equal_to(level_2_hash)
        assert_that(row2[PARENT_ID]).is_equal_to(row3[ROW_ID])
        assert_that(row2[PARENT_ID]).is_equal_to(level_1_hash)

        assert_that(row3[NAME]).is_equal_to(ROOT)
        assert_that(row3[TABLE]).is_equal_to(level_1_value)
        assert_that(row3[ROW_ID]).is_equal_to(level_1_hash)
        assert_that(row3[PARENT_ID]).is_none()


    @pytest.mark.parametrize("unique_id", [(''), 
                                        ('abc'),
                                        (None)],
                            ids=['empty', 'some_string', 'None'])
    def test__destructure__different_seeds__row_id_is_different(self, d_hasher: DictionaryHasher, unique_id):
        destructor = Destructor(d_hasher, unique_id)
        data = {"a": 1, "b": 2, "c": 3}

        result = destructor.destructure(data)[0]

        assert_that(result[NAME]).is_equal_to(ROOT)
        assert_that(result[TABLE]).is_equal_to(data)
        assert_that(result[ROW_ID]).is_equal_to(d_hasher.hash(data, unique_id))
        assert_that(result[PARENT_ID]).is_none()


    @pytest.mark.parametrize("values", [([]), 
                                        (['x', '9', 'y']),
                                        ({"x": 9})],
                            ids=['empty_list', 'primitive_list', 'primitive_dict'])
    def test__destructure__dict_with_empty_list__destructured(self, d_hasher: DictionaryHasher, values):
        destructor = Destructor(d_hasher)
        target_key, target_value = 'c', values
        data = {"a": 1, "b": 2, target_key: target_value}
        result = destructor.destructure(data)

        row1, row2 = result[0], result[1]
        assert_that(row1[NAME]).is_equal_to(target_key)
        assert_that(row1[TABLE]).is_equal_to(target_value)
        assert_that(row1[ROW_ID]).is_equal_to(d_hasher.hash(target_value))
        assert_that(row1[PARENT_ID]).is_equal_to(row2[ROW_ID])

        expected_root_data = {k: v for k, v in data.items() if k != target_key}
        assert_that(row2[NAME]).is_equal_to(ROOT)
        assert_that(row2[TABLE]).is_equal_to(expected_root_data)
        assert_that(row2[ROW_ID]).is_equal_to(d_hasher.hash(data))
        assert_that(row2[PARENT_ID]).is_none()


    # Fuzz test case ({'x": 9}'})],
    def test__destructure__dict_with_complex_list__destructured(self, d_hasher: DictionaryHasher):
        """This test is close to the data we would see."""
        target_key, target_value = 'c', [{"x": 9}]
        data = {"a": 1, "b": 2, target_key: target_value}
        destructor = Destructor(d_hasher)

        result = destructor.destructure(data)

        row1, row2 = result[0], result[1]
        assert_that(row1[NAME]).is_equal_to(target_key)
        assert_that(row1[TABLE]).is_equal_to(*target_value)
        assert_that(row1[ROW_ID]).is_equal_to(d_hasher.hash(*target_value))
        assert_that(row1[PARENT_ID]).is_equal_to(row2[ROW_ID])

        expected_root_data = {k: v for k, v in data.items() if k != target_key}
        assert_that(row2[NAME]).is_equal_to(ROOT)
        assert_that(row2[TABLE]).is_equal_to(expected_root_data)
        assert_that(row2[ROW_ID]).is_equal_to(d_hasher.hash(data, ''))
        assert_that(row2[PARENT_ID]).is_none()



    @unittest.skip("todo") # More of an integration test.  Replace hardcoded json.
    def test__destructure__json__destructured(self, d_hasher: DictionaryHasher):
        """This test is accurate to the data we could see."""
        destructor = Destructor(d_hasher)

        import os
        cur_dir = os.path.dirname(os.path.abspath(__file__))
        jsonl_path = f"{cur_dir}/../tests/some.jsonl"

        with open(jsonl_path, 'r') as f:
            data = json.load(f)

        result = destructor.destructure(data)

        assert_that(result).is_not_none()
        # TODO:  More assertions


