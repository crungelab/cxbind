from typing import List

from .context import GeneratorContext


class Argument:
    def __init__(self, context: GeneratorContext, node) -> None:
        self.context = context
        self.node = node

    @property
    def name(self):
        return self.node.spelling
    
    @property
    def type(self):
        return self.node.type

    @property
    def arg_type(self):
        return self.context.arg_type(self.node)

class ArgumentList:
    def __init__(self, context: GeneratorContext, node) -> None:
        self.context = context
        self.node = node
        self.arguments: List[Argument] = []
        #args = [a for a in node.get_arguments()]
        args = node.get_arguments()
        for arg in args:
            self.arguments.append(Argument(context, arg))

    def arg_types(self):
        return [a.arg_type for a in self.arguments]
    
    def arg_names(self, arguments):
        return ', '.join([self.context.arg_name(a) for a in arguments])

    
    def to_string(self):
        return ', '.join(['{} {}'.format(a.arg_type, a.name) for a in self.arguments])
