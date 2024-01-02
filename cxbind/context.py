import re

from clang import cindex

class EntryContext:
    def __init__(self) -> None:
        self.prefix = ''
        self.short_prefix = ''

    @classmethod
    def spell(cls, node: cindex.Cursor):
        if node is None:
            return ''
        elif node.kind == cindex.CursorKind.TRANSLATION_UNIT:
            return ''
        else:
            res = cls.spell(node.semantic_parent)
            if res != '':
                return res + '::' + node.spelling
        return node.spelling

    @classmethod
    def snake(cls, name: str):
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
        #return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()
        return re.sub('([a-z])([A-Z])', r'\1_\2', s1).lower()

    @classmethod
    def format_field(cls, name: str):
        name = cls.snake(name)
        name = name.rstrip('_')
        name = name.replace('__', '_')
        return name

    def format_type(self, name: str):
        #name = name.replace(self.prefix, '')
        name = name.replace(self.prefix, '', 1)
        #name = name.replace(self.short_prefix, '')
        name = name.replace(self.short_prefix, '', 1)
        name = name.replace('<', '_')
        name = name.replace('>', '')
        name = name.replace(' ', '')
        name = name.rstrip('_')
        return name

    def format_enum(self, name: str):
        #name = name.replace(self.prefix, '')
        name = name.replace(self.prefix, '', 1)
        #name = name.replace(self.short_prefix, '')
        name = name.replace(self.short_prefix, '', 1)
        name = self.snake(name).upper()
        name = name.replace('__', '_')
        name = name.rstrip('_')
        return name
