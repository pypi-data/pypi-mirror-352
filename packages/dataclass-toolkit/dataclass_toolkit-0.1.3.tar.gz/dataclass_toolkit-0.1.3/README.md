# dataclass_toolkit

> Minimalistic utilities for working with Python `dataclass` — serialize, deserialize, and compactly store dataclass instances.

[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/dataclass_toolkit)](https://pypi.org/project/dataclass_toolkit/)
[![PyPI - Version](https://img.shields.io/pypi/v/dataclass_toolkit.svg)](https://pypi.org/project/dataclass_toolkit/)

---

## Installation

```bash
pip install dataclass_toolkit
```

---

## What is dataclass_toolkit?

**dataclass_toolkit** provides lightweight tools to work with Python dataclasses:

- Convert dataclass instances into compact lists.
- Restore dataclasses from lists.
- Handle nested dataclasses and lists of dataclasses automatically.
- Save and transmit dataclass data in the most compact way.

---

## Example Usage

```python
from dataclasses import dataclass
from dataclass_toolkit.as_list import serialize_dataclass_to_list, deserialize_list_to_dataclass

@dataclass
class Child:
    x: int
    y: str

@dataclass
class Parent:
    a: int
    b: Child
    c: list[Child]

# Create an object
p = Parent(
    a=1,
    b=Child(x=10, y="hello"),
    c=[Child(x=20, y="world")]
)

# Serialize to list
data = serialize_dataclass_to_list(p)
print(data)
# Output: [1, [10, 'hello'], [[20, 'world']]]

# Deserialize back
restored = deserialize_list_to_dataclass(Parent, data)
print(restored)
# Output: Parent(a=1, b=Child(x=10, y='hello'), c=[Child(x=20, y='world')])
```

---

## 🔥 Features

- ✅ Supports nested dataclasses
- ✅ Supports lists of dataclasses
- ✅ Compatible with `__slots__`
- ✅ Minimal and efficient serialization
- ✅ Clean and extensible codebase

---

## 📜 License

This project is licensed under the **MIT License** — feel free to use it in your projects!

---

## 🤝 Contributing

Pull requests are welcome!  
If you have ideas for improvements or new utilities, feel free to open an issue.
