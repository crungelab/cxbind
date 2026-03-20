from typing import TypeVar, Generic, Dict, Optional, Callable
from .entry import EntryKey, Entry

T_Entry = TypeVar("T_Entry", bound=Entry)

class EntryRegistry(Generic[T_Entry]):
    def __init__(self) -> None:
        self.entries_by_key: dict[EntryKey, T_Entry] = {}
        self.entries: list[T_Entry] = []

    def __iter__(self):
        return iter(self.entries)
        
    @classmethod
    def from_entries(cls, entries: dict[EntryKey, T_Entry]) -> "EntryRegistry[T_Entry]":
        registry = cls()
        for entry in entries.values():
            registry.register(entry)
        return registry

    def register(self, entry: T_Entry) -> None:
        key = entry.key
        if key in self.entries_by_key:
            raise KeyError(f"Duplicate entry key: {key}")

        self.entries_by_key[key] = entry
        self.entries.append(entry)

    def get(self, key: EntryKey) -> T_Entry | None:
        return self.entries_by_key.get(key)

    def require(self, key: EntryKey) -> T_Entry:
        entry = self.get(key)
        if entry is None:
            raise KeyError(f"Unknown entry key: {key}")
        return entry
