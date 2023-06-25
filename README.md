# destructure
Python module that destructures or normalizes a JSON object.  There are generally two ways to transform json into a table like structure.  Option 1, you can flatten the json (https://github.com/amirziai/flatten) and generate unique IDs based off the values within the array. Option 2, you can destructure the JSON by pulling out each nested level.

Option 1 output example:

```json
{"__id__" = "b3a0351cf4033d9484363bb6d4092d28" "id": "01", "name": "Jeff", "department_name": "Strategic Hazard Intervention Espionage Logistics Directorate", "department_locations_0": "Fort Meade, Maryland, U.S. 39°6′32″N 76°46′17″W", "department_locations_1": "Seattle, WA"}
```

Option 2 is more suitable if you want to query the data in a relational manner.  The `__id__` is an identifying hash based off each nested JSON level.


### Usage
See the unit tests for more examples.

```python
import json

d_hasher = DictionaryHasher()
destructor = Destructor(d_hasher)
json_str = '{"id":"01", "name": "Jeff", "department": {"name": "Strategic Hazard Intervention Espionage Logistics Directorate", "location": "Fort Meade, Maryland, U.S. 39°6′32″N 76°46′17″W" } }'
data  = json.loads(json_str)
list_of_dicts = destructor.destructure(data)


```

Output:

```sh
{'__name__': 'department', '__table__': {'name': 'Strategic Hazard Intervention Espionage Logistics Directorate': 'Fort Meade, Maryland, U.S. 39°6′32″N 76°46′17″W'}, '__id__': 'b3a0351cf4033d9484363bb6d4092d28', '__parent_id__': '5249f69db1e9a8a009e43f27596eacca'}

{'__name__': '__root__', '__table__': {'id': '01', 'name': 'Jeff'}, '__id__': '5249f69db1e9a8a009e43f27596eacca', '__parent_id__': None}
```

The `__name__` is name of the JSON property which can be used as a table name.  The `__table__` contains the primitive types that can be applied to something like a SQL table or [Delta Lake Table](https://delta.io/).  The `__parent_id__` is the `__id__` of the parent property or can be thought of as the `Foreign Key`.