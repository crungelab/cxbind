from typing import TypeVar, Generic, Dict, Optional, Callable
from .entry import EntryKey, Entry

T_Entry = TypeVar("T_Entry", bound=Entry)

class EntryRegistry(Generic[T_Entry]):
    def __init__(self) -> None:
        self._by_key: dict[EntryKey, T_Entry] = {}
        self._by_name: dict[str, T_Entry | None] = {}
        self._by_kind_name: dict[tuple[str, str], T_Entry | None] = {}

    @classmethod
    def from_entries(cls, entries: dict[EntryKey, T_Entry]) -> "EntryRegistry[T_Entry]":
        registry = cls()
        for entry in entries.values():
            registry.register(entry)
        return registry

    def register(self, entry: T_Entry) -> None:
        key = entry.key
        if key in self._by_key:
            raise KeyError(f"Duplicate entry key: {key}")

        self._by_key[key] = entry

        if entry.name not in self._by_name:
            self._by_name[entry.name] = entry
        else:
            self._by_name[entry.name] = None

        kind_name = (entry.kind, entry.name)
        if kind_name not in self._by_kind_name:
            self._by_kind_name[kind_name] = entry
        else:
            self._by_kind_name[kind_name] = None

    def get(self, key: EntryKey) -> T_Entry | None:
        return self._by_key.get(key)

    def require(self, key: EntryKey) -> T_Entry:
        entry = self.get(key)
        if entry is None:
            raise KeyError(f"Unknown entry key: {key}")
        return entry

    def get_by_name(self, name: str) -> T_Entry | None:
        return self._by_name.get(name)

    def get_by_kind_name(self, kind: str, name: str) -> T_Entry | None:
        return self._by_kind_name.get((kind, name))

    def find(
        self,
        *,
        name: str,
        kind: str | None = None,
        signature: str | None = None,
    ) -> list[T_Entry]:
        matches = [entry for entry in self._by_key.values() if entry.name == name]

        if kind is not None:
            matches = [entry for entry in matches if entry.kind == kind]

        if signature is not None:
            matches = [entry for entry in matches if entry.signature == signature]

        return matches

    def resolve(
        self,
        *,
        name: str,
        kind: str | None = None,
        signature: str | None = None,
    ) -> T_Entry | None:
        if kind is not None:
            exact = self.get(EntryKey.build(kind=kind, name=name, signature=signature))
            if exact is not None:
                return exact

            if signature is None:
                return self.get_by_kind_name(kind, name)

            return None

        if signature is None:
            return self.get_by_name(name)

        matches = self.find(name=name, signature=signature)
        if not matches:
            return None
        if len(matches) == 1:
            return matches[0]

        raise KeyError(
            f"Ambiguous entry lookup for "
            f"name={name!r}, kind={kind!r}, signature={signature!r}: "
            f"{[entry.key_string for entry in matches]}"
        )
