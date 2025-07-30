from dataclasses import is_dataclass, fields, Field
from typing import Any, Type, TypeVar, get_origin, get_args, Union, cast

try:
    from types import UnionType
except ImportError:
    UnionType = Union

T = TypeVar('T')


def serialize_dataclass_to_list(obj: Any) -> list[Any]:
    """
    Serialize a dataclass instance into a flat list of its field values.

    This function recursively serializes fields that are themselves dataclasses,
    and also properly handles lists of dataclasses.

    Supports both regular dataclasses and dataclasses that use __slots__.

    Args:
        obj (Any): The dataclass instance to serialize.

    Returns:
        List[Any]: A list representing the serialized fields of the dataclass,
        preserving nested structures.

    Raises:
        ValueError: If the input is not a dataclass instance.

    Example:
        >>> @dataclass
        ... class Child:
        ...     x: int
        ...     y: str
        ...
        >>> @dataclass
        ... class Parent:
        ...     a: int
        ...     b: Child
        ...     c: list[Child]
        ...
        >>> p = Parent(a=1, b=Child(x=10, y="hello"), c=[Child(x=20, y="world")])
        >>> serialize_dataclass_to_list(p)
        [1, [10, 'hello'], [[20, 'world']]]
    """
    if not is_dataclass(obj):
        raise ValueError(f"Expected dataclass instance, got {type(obj)}")

    result = []
    for f in fields(obj):
        value = getattr(obj, f.name)
        if value is None:
            result.append(None)
        elif is_dataclass(value):
            result.append(serialize_dataclass_to_list(value))
        elif isinstance(value, list):
            if value and all(is_dataclass(item) for item in value):
                result.append([serialize_dataclass_to_list(item) for item in value])
            else:
                result.append(value)
        else:
            result.append(value)
    return result


def deserialize_list_to_dataclass(cls: Any, data: list[Any]) -> T:
    """
    Deserialize a list of values into a dataclass instance.

    This function reconstructs nested dataclasses and lists of dataclasses
    if the dataclass structure requires it.

    Supports both regular dataclasses and dataclasses with __slots__.

    Args:
        cls (Type[T]): The dataclass type to instantiate.
        data (List[Any]): The list of values representing the serialized fields.

    Returns:
        T: An instance of the dataclass reconstructed from the provided list.

    Raises:
        ValueError: If cls is not a dataclass or if the number of fields and values do not match.

    Example:
        >>> @dataclass
        ... class Child:
        ...     x: int
        ...     y: str
        ...
        >>> @dataclass
        ... class Parent:
        ...     a: int
        ...     b: Child
        ...     c: list[Child]
        ...
        >>> data = [1, [10, 'hello'], [[20, 'world']]]
        >>> deserialize_list_to_dataclass(Parent, data)
        Parent(a=1, b=Child(x=10, y='hello'), c=[Child(x=20, y='world')])
    """
    if not is_dataclass(cls):
        raise ValueError(f"Expected dataclass class, got {cls}")

    cls_fields: tuple[Field[Any], ...] = fields(cls)

    if len(data) != len(cls_fields):
        raise ValueError(f"Field count mismatch: expected {len(cls_fields)}, got {len(data)}")

    init_kwargs: dict[str, Any] = {}

    for field_obj, value in zip(cls_fields, data):
        field_type = field_obj.type

        if value is None:
            init_kwargs[field_obj.name] = None
            continue

        origin = get_origin(field_type)

        # Handle list fields
        if origin is list:
            inner_type = _extract_dataclass_type(get_args(field_type)[0])
            if is_dataclass(inner_type):
                init_kwargs[field_obj.name] = [
                    deserialize_list_to_dataclass(inner_type, item) for item in value
                ]
            else:
                init_kwargs[field_obj.name] = value
        # Handle nested dataclass
        elif _is_nested_dataclass(field_type):
            inner_type = _extract_dataclass_type(field_type)
            init_kwargs[field_obj.name] = deserialize_list_to_dataclass(inner_type, value)
        else:
            init_kwargs[field_obj.name] = value

    return cast(T, cls(**init_kwargs))


def _is_nested_dataclass(typ: Any) -> bool:
    origin = get_origin(typ)
    if origin in (Union, UnionType):
        return any(is_dataclass(arg) for arg in get_args(typ) if arg is not type(None))
    return is_dataclass(typ)


def _extract_dataclass_type(typ: Any) -> Type[Any]:
    origin = get_origin(typ)
    if origin in (Union, UnionType):
        for arg in get_args(typ):
            if arg is not type(None) and is_dataclass(arg):
                return arg
        raise ValueError(f"No dataclass found in Union: {typ}")
    return typ
