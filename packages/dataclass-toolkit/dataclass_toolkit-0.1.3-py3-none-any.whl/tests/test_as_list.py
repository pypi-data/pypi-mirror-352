import pytest
from dataclasses import dataclass
from typing import List
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from dataclass_toolkit.as_list import serialize_dataclass_to_list, deserialize_list_to_dataclass


@dataclass
class Simple:
    x: int
    y: str


@dataclass
class Nested:
    a: int
    b: Simple


@dataclass
class NestedOptional:
    a: int
    b: Nested | None


@dataclass
class WithList:
    items: List[Simple]


@dataclass
class DeepNested:
    items: List[Nested]


@dataclass
class DeepWithList:
    items: List[WithList]


def test_simple_dataclass():
    obj = Simple(x=10, y="hello")
    serialized = serialize_dataclass_to_list(obj)
    assert serialized == [10, "hello"]

    restored = deserialize_list_to_dataclass(Simple, serialized)
    assert restored == obj


def test_nested_dataclass():
    obj = Nested(a=1, b=Simple(x=2, y="world"))
    serialized = serialize_dataclass_to_list(obj)
    assert serialized == [1, [2, "world"]]

    restored = deserialize_list_to_dataclass(Nested, serialized)
    assert restored == obj


def test_list_of_dataclasses():
    obj = WithList(items=[Simple(x=1, y="a"), Simple(x=2, y="b")])
    serialized = serialize_dataclass_to_list(obj)
    assert serialized == [[[1, "a"], [2, "b"]]]

    restored = deserialize_list_to_dataclass(WithList, serialized)
    assert restored == obj


def test_list_to_nested_optional():
    simple1 = Simple(x=10, y="hello")
    nested = Nested(a=30, b=simple1)
    nested_optional = NestedOptional(a=20, b=nested)
    serialized = serialize_dataclass_to_list(nested_optional)
    assert serialized == [20, [30, [10, "hello"]]]
    unserialized = deserialize_list_to_dataclass(NestedOptional, serialized)
    assert unserialized == nested_optional


def test_invalid_serialize_non_dataclass():
    with pytest.raises(ValueError):
        serialize_dataclass_to_list({"not": "a dataclass"})


def test_invalid_deserialize_non_dataclass():
    with pytest.raises(ValueError):
        deserialize_list_to_dataclass(dict, [])


def test_field_count_mismatch():
    with pytest.raises(ValueError):
        deserialize_list_to_dataclass(Simple, [1])


def test_deep_nested_dataclass():
    simple_10 = Simple(x=10, y="ten")
    simple_20 = Simple(x=20, y="twenty")
    nested_10 = Nested(a=1, b=simple_10)
    nested_20 = Nested(a=2, b=simple_20)
    deep_nested = DeepNested(items=[nested_10, nested_20])
    list_deep_nested = serialize_dataclass_to_list(deep_nested)
    assert list_deep_nested == [[[1, [10, 'ten']], [2, [20, 'twenty']]]]
    new_deep_nested = deserialize_list_to_dataclass(DeepNested, list_deep_nested)
    assert new_deep_nested == deep_nested
    assert new_deep_nested is not deep_nested


def test_deep_with_list_dataclass():
    simple_10 = Simple(x=10, y="ten")
    simple_20 = Simple(x=20, y="twenty")
    simple_30 = Simple(x=30, y="thirty")
    simple_40 = Simple(x=40, y="fourth")
    with_list_1 = WithList(items=[simple_10, simple_20])
    with_list_2 = WithList(items=[simple_30, simple_40])
    deep_with_list = DeepWithList(items=[with_list_1, with_list_2])
    list_deep_with_list = serialize_dataclass_to_list(deep_with_list)
    assert list_deep_with_list == [[[[[10, 'ten'], [20, 'twenty']]], [[[30, 'thirty'], [40, 'fourth']]]]]
    new_deep_with_list = deserialize_list_to_dataclass(DeepWithList, list_deep_with_list)
    assert new_deep_with_list == deep_with_list
    assert new_deep_with_list is not deep_with_list
