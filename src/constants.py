import numbers
from typing import Dict, List, Optional, Union


ROW_ID = '__id__'
PARENT_ID = '__parent_id__'

NAME = '__name__'
TABLE = '__table__'

ID = 'Id'
FILE_ID = 'FileId'
ROOT = '__root__'

JSON = 'json'


ExpectedTypes = Union[str, numbers.Number, bool, List, Dict[str, 'ExpectedTypes']] # ignore: type

DestructureType = Dict[str, Union[Optional[ExpectedTypes], 'DestructureType']] # ignore: type