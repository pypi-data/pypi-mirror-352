# Overview

## Installation

``` bash
pip install ncw
```


## Basic usage

The **Structure** class prevents accidental changes to the underlying data structure
by preventing direct access.
All returned substructures are deep copies of the internally stored substructures.

The **MutableStructure** class allows changes (ie. deletions and updates)
to the underlying data structure, and returns the internally stored substructures themselves.

Please note that both classes make a deep copy of the data structure at initialization time
(thus preventing accidental changes to the original data through the instance).

``` pycon
>>> serialized = '{"herbs": {"common": ["basil", "oregano", "parsley", "thyme"], "disputed": ["anise", "coriander"]}}'
>>>
>>> import json
>>> original_data = json.loads(serialized)
>>>
>>> from ncw import Structure, MutableStructure
>>>
>>> readonly = Structure(original_data)
>>> readonly["herbs"]
{'common': ['basil', 'oregano', 'parsley', 'thyme'], 'disputed': ['anise', 'coriander']}
>>> readonly["herbs.common"]
['basil', 'oregano', 'parsley', 'thyme']
>>> readonly["herbs", "common"]
['basil', 'oregano', 'parsley', 'thyme']
>>> readonly["herbs", "common", 1]
'oregano'
>>> readonly["herbs.common.1"]
'oregano'
>>> readonly["herbs.common.1"] = "marjoram"
Traceback (most recent call last):
  File "<python-input-9>", line 1, in <module>
    readonly["herbs.common.1"] = "marjoram"
    ~~~~~~~~^^^^^^^^^^^^^^^^^^
TypeError: 'Structure' object does not support item assignment
>>>
>>> writable = MutableStructure(original_data)
>>> writable.data == original_data
True
>>> writable.data is original_data
False
>>> writable["herbs.common.1"]
'oregano'
>>> writable["herbs.common.1"] = "marjoram"
>>> del writable["herbs", "common", 2]
>>> writable["herbs.common"]
['basil', 'marjoram', 'thyme']
>>>
```
