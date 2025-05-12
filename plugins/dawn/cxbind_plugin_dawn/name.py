name_table = {}

class Name:
    def __init__(self, name, native=False):
        self.native = native
        self.name = name
        if native:
            self.chunks = [name]
        else:
            self.chunks = name.split(' ')

    def get(self):
        return self.name

    @classmethod
    def intern(cls, name: str, native: bool = False) -> 'Name':
        if name not in name_table:
            name_table[name] = cls(name, native)
        return name_table[name]

    @staticmethod
    def CamelChunk(chunk: str) -> str:
        return chunk[0].upper() + chunk[1:]

    def canonical_case(self) -> str:
        return ' '.join(self.chunks)

    def concatcase(self) -> str:
        return ''.join(self.chunks)

    def camelCase(self) -> str:
        return self.chunks[0] + ''.join(
            [self.CamelChunk(chunk) for chunk in self.chunks[1:]])

    def CamelCase(self) -> str:
        return ''.join([self.CamelChunk(chunk) for chunk in self.chunks])

    def SNAKE_CASE(self) -> str:
        return '_'.join([chunk.upper() for chunk in self.chunks])

    def snake_case(self) -> str:
        return '_'.join(self.chunks)

    def namespace_case(self) -> str:
        return '::'.join(self.chunks)

    def Dirs(self) -> str:
        return '/'.join(self.chunks)

    def js_enum_case(self) -> str:
        result = self.chunks[0].lower()
        for chunk in self.chunks[1:]:
            if not result[-1].isdigit():
                result += '-'
            result += chunk.lower()
        return result

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v, info):
        if isinstance(v, cls):
            return v
        if not isinstance(v, str):
            raise TypeError('string required')
        return cls(v)

    def __str__(self):
        return self.name

    def __repr__(self):
        return f"Name({self.name!r})"