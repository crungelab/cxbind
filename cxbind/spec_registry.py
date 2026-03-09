from .spec import SpecKey, SpecUnion


class SpecRegistry:
    def __init__(self) -> None:
        self._by_key: dict[SpecKey, SpecUnion] = {}
        self._by_name: dict[str, SpecUnion | None] = {}
        self._by_kind_name: dict[tuple[str, str], SpecUnion | None] = {}

    @classmethod
    def from_specs(cls, specs: dict[SpecKey, SpecUnion]) -> "SpecRegistry":
        registry = cls()
        for spec in specs.values():
            registry.register(spec)
        return registry

    def register(self, spec: SpecUnion) -> None:
        key = spec.key
        if key in self._by_key:
            raise KeyError(f"Duplicate spec key: {key}")

        self._by_key[key] = spec

        if spec.name not in self._by_name:
            self._by_name[spec.name] = spec
        else:
            self._by_name[spec.name] = None

        kind_name = (spec.kind, spec.name)
        if kind_name not in self._by_kind_name:
            self._by_kind_name[kind_name] = spec
        else:
            self._by_kind_name[kind_name] = None

    def get(self, key: SpecKey) -> SpecUnion | None:
        return self._by_key.get(key)

    def require(self, key: SpecKey) -> SpecUnion:
        spec = self.get(key)
        if spec is None:
            raise KeyError(f"Unknown spec key: {key}")
        return spec

    def get_by_name(self, name: str) -> SpecUnion | None:
        return self._by_name.get(name)

    def get_by_kind_name(self, kind: str, name: str) -> SpecUnion | None:
        return self._by_kind_name.get((kind, name))

    def find(
        self,
        *,
        name: str,
        kind: str | None = None,
        signature: str | None = None,
    ) -> list[SpecUnion]:
        matches = [spec for spec in self._by_key.values() if spec.name == name]

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
            exact = self.get(SpecKey.build(kind=kind, name=name, signature=signature))
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
            f"Ambiguous spec lookup for "
            f"name={name!r}, kind={kind!r}, signature={signature!r}: "
            f"{[spec.key_string for spec in matches]}"
        )
