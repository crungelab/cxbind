from .function_base_builder import FunctionBaseBuilder
from ..node import Function


class FunctionBuilder(FunctionBaseBuilder[Function]):
    def create_node(self):
        self.node = Function(self.fqname, self.cursor)

    def build_node(self):
        super().build_node()
        
        node = self.node
        cursor = self.cursor
        mname = self.scope
        arguments = [a for a in cursor.get_arguments()]
        cname = "&" + self.spell(cursor)
        pyname = self.format_field(cursor.spelling)
        if self.is_overloaded(cursor):
            cname = f"py::overload_cast<{self.arg_types(arguments)}>({cname})"
        if self.should_wrap_function(cursor):
            self(f'{mname}.def("{pyname}", []({self.arg_string(arguments)})')
            self("{")
            ret = "" if self.is_function_void_return(cursor) else "auto ret = "

            result = f"{self.spell(cursor)}({self.arg_names(arguments)})"
            result_type = cursor.result_type
            #logger.debug(f'result_type: {result_type.spelling}')
            result_type_name = result_type.spelling.split(' ')[0]

            if result_type_name in self.wrapped:
                result_type_name = self.wrapped[result_type_name].gen_wrapper['type']
                result = f"new {result_type_name}({result})"

            with self:
                self(f"{ret}{result};")
                self(f"return {self.get_function_result(node, cursor)};")
            self("}")
        else:
            self(f'{mname}.def("{pyname}", {cname}')
        self.write_pyargs(arguments, node)
        self(f", {self.get_return_policy(cursor)});\n")
