from typing import TYPE_CHECKING, Dict, List
if TYPE_CHECKING:
    from cxbind.entry import Entry

import re

from clang import cindex
from loguru import logger

class GeneratorContext:
    def __init__(self) -> None:
        self.prefixes = None
        self.wrapped: Dict[Entry] = {}

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
        return re.sub('([a-z])([A-Z])', r'\1_\2', s1).lower()

    def strip_prefixes(self, name: str):
        #logger.debug(f"prefixes: {self.prefixes}")
        if isinstance(self.prefixes, str):
            name = name.replace(self.prefixes, '', 1)
        elif isinstance(self.prefixes, list):
            for prefix in self.prefixes:
                name = name.replace(prefix, '', 1)
        return name
    
    def format_field(self, name: str):
        name = self.strip_prefixes(name)
        name = self.snake(name)
        name = name.rstrip('_')
        name = name.replace('__', '_')
        return name

    def format_type(self, name: str):
        name = self.strip_prefixes(name)
        name = name.replace('<', '_')
        name = name.replace('>', '')
        name = name.replace(' ', '')
        name = name.rstrip('_')
        return name

    def format_enum(self, name: str):
        name = self.strip_prefixes(name)
        name = self.snake(name).upper()
        name = name.replace('__', '_')
        name = name.rstrip('_')
        return name

    def arg_type(self, argument):
        if argument.type.kind == cindex.TypeKind.CONSTANTARRAY:
            return f'std::array<{argument.type.get_array_element_type().spelling}, {argument.type.get_array_size()}>&'
        
        type_name = argument.type.spelling.split(' ')[0]
        if  type_name in self.wrapped:
            return argument.type.spelling.replace(type_name, self.wrapped[type_name].gen_wrapper['type'])

        return argument.type.spelling

    def arg_name(self, argument):
        if argument.type.kind == cindex.TypeKind.CONSTANTARRAY:
            return f'&{argument.spelling}[0]'
        return argument.spelling

    def arg_types(self, arguments):
        return ', '.join([self.arg_type(a) for a in arguments])

    def arg_names(self, arguments: List[cindex.Cursor]):
        returned = []
        for a in arguments:
            type_name = a.type.spelling.split(' ')[0]
            if type_name in self.wrapped:
                returned.append(f"{self.arg_name(a)}->get()")
            else:
                returned.append(self.arg_name(a))
        return ', '.join(returned)

    '''
    def arg_names(self, arguments):
        return ', '.join([self.arg_name(a) for a in arguments])
    '''

    def arg_string(self, arguments):
        return ', '.join(['{} {}'.format(self.arg_type(a), a.spelling) for a in arguments])
