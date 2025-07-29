# Glossary of terms

## Nested Collection

_tl;dr:_ what is returned e.g. from the standard library’s
[json.load()] or [json.loads()] functions.


## Structure

A Wrapper around a [Nested Collection] providing readonly access.

A deep copy of the original [Nested Collection] is available through the **.data**
attribute.

The **.get()** method or item access (through `instance[index]`)
always return deep copies of the substructures determined by the provided index
(of type [IndexType]).


## MutableStructure

Subclass of [Structure]:
a Wrapper around a [Nested Collection] providing read and write access.

The **.get()** method and item access return the substructure itself instead of a copy.

Additionally, **.delete()** and **.update()** methods are provided as well as
`del instance[index]` and `instance[index] = …` capabilities changing the
underlying data structure in place.

The **.data** attribute is initially a deep copy of the original [Nested Collection],
but this data structure can be modified either through the possibilities mentioned
in the previous paragraph, or directly.


## Types

### CollectionType

A **dict** or **list** instance.


### ScalarType

An immutable value, either `None` or a **str**, **float**, **int**, or **bool**
instance. Sutable as keys for **dict** instances in [nested collections][Nested Collection].


### ValueType

A [CollectionType] or [ScalarType] instance, suitable as a value for **dict**
or **list** instances in [nested collections][Nested Collection].


### SegmentsTuple

A **tuple** of [ScalarType] instances
(used by the **commons.partial_traverse()** and **commons.full_traverse()** functions)


### IndexType

A [SegmentsTuple] or a **str** instance.

May be used as a traversal path in [Structure] or [MutableStructure] instances,
ie. for adressing any [ValueType] contained in the underlying [nested collection][Nested Collection].


* * *
[Nested Collection]: #nested-collection
[json.load()]: https://docs.python.org/3/library/json.html#json.load
[json.loads()]: https://docs.python.org/3/library/json.html#json.loads
[Structure]: #structure
[MutableStructure]: #mutablestructure
[CollectionType]: #collectiontype
[ScalarType]: #scalartype
[ValueType]: #valuetype
[SegmentsTuple]: #segmentstuple
[IndexType]: #indextype
