from .spec import EntryKey, SpecUnion


class SpecRegistry:
    def __init__(self) -> None:
        self._specs: dict[EntryKey, SpecUnion] = {}
        self._by_name: dict[str, SpecUnion] = {}

    @property
    def specs(self) -> dict[EntryKey, SpecUnion]:
        return self._specs

    def register(self, spec: SpecUnion) -> None:
        key = spec.key
        if key in self._specs:
            raise KeyError(f"Duplicate spec key: {key}")

        self._specs[key] = spec

        # secondary index by fully-qualified name only when unique
        existing = self._by_name.get(spec.name)
        if existing is None:
            self._by_name[spec.name] = spec
        else:
            # multiple specs may share the same fully-qualified name
            # e.g. overloaded functions/methods, so remove uniqueness
            del self._by_name[spec.name]
    
    def register_many(self, specs: list[SpecUnion]) -> None:
        for spec in specs:
            self.register(spec)

    def get(self, key: EntryKey) -> SpecUnion | None:
        return self._specs.get(key)

    def require(self, key: EntryKey) -> SpecUnion:
        spec = self.get(key)
        if spec is None:
            raise KeyError(f"Unknown spec key: {key}")
        return spec

    def get_by_name(self, name: str) -> SpecUnion | None:
        return self._by_name.get(name)

    def require_by_name(self, name: str) -> SpecUnion:
        spec = self.get_by_name(name)
        if spec is None:
            matches = self.find_by_name(name)
            if not matches:
                raise KeyError(f"No spec found for name: {name}")
            raise KeyError(
                f"Ambiguous spec lookup for name={name!r}: {[str(spec.key) for spec in matches]}"
            )
        return spec

    def find_by_name(
        self,
        name: str,
        *,
        kind: str | None = None,
    ) -> list[SpecUnion]:
        matches = [spec for spec in self._specs.values() if spec.name == name]
        if kind is not None:
            matches = [spec for spec in matches if spec.kind == kind]
        return matches

    def find(
        self,
        *,
        name: str,
        kind: str | None = None,
        signature: str | None = None,
    ) -> list[SpecUnion]:
        matches = [spec for spec in self._specs.values() if spec.name == name]

        if kind is not None:
            matches = [spec for spec in matches if spec.kind == kind]

        if signature is not None:
            matches = [spec for spec in matches if spec.signature == signature]

        return matches

    def resolve(
        self,
        *,
        name: str,
        kind: str | None = None,
        signature: str | None = None,
    ) -> SpecUnion | None:
        if kind is not None:
            exact = self.get(EntryKey.build(kind=kind, name=name, signature=signature))
            if exact is not None:
                return exact

        matches = self.find(name=name, kind=kind, signature=signature)

        if not matches:
            return None
        if len(matches) == 1:
            return matches[0]

        raise KeyError(
            f"Ambiguous spec lookup for "
            f"name={name!r}, kind={kind!r}, signature={signature!r}: "
            f"{[str(spec.key) for spec in matches]}"
        )
