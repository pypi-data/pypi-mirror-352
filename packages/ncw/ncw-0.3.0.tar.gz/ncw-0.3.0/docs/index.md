# Overview

_Nested collections wrapper_


## Purpose

!!! tip ""

    Preventing square brackets overkill

Read or modify data in nested collections with simplified addressing,
e.g. to replace

``` python
value = nested_collection["data"]{"attributes"}["parent"]["id"]
```

by

``` python
value = structure["data.attributes.parent.id"]
```

or

``` python
value = structure["data", "attributes", "parent", "id"]
```


## Installation

``` bash
pip install ncw
```


## Basic usage

The **[Structure]** class prevents accidental changes to the underlying data structure
by preventing direct access.
All returned substructures are deep copies of the internally stored substructures.

The **[MutableStructure]** class allows changes (ie. deletions and updates)
to the underlying data structure, and returns the internally stored substructures themselves.

!!! note

    Both classes do not store the data structure provided a initialization itself
    but a deep copy of it – in order to prevent accidental changes to the original data.

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

* * *
[Structure]: 5-glossary.md#structure
[MutableStructure]: 5-glossary.md##mutablestructure

