from .function_base_builder import FunctionBaseBuilder
from ..node import MethodNode


class MethodBuilder(FunctionBaseBuilder[MethodNode]):
    def should_cancel(self):
        if self.top_node is None:
            return True
        return super().should_cancel()

    def create_node(self):
        self.node = MethodNode(name=self.name, cursor=self.cursor)

    def build_node(self):
        super().build_node()
        
        node = self.node
        cursor = self.cursor
        mname = self.scope
        arguments = [a for a in cursor.get_arguments()]
        cname = "&" + self.spell(cursor)
        pyname = self.format_field(cursor.spelling)
        if self.is_overloaded(cursor):
            extra = ""
            if cursor.is_const_method():
                extra = ", py::const_"
            cname = f"py::overload_cast<{self.arg_types(arguments)}>({cname}{extra})"
        if self.should_wrap_function(cursor):
            #self.out(f'{mname}.def("{pyname}", []({self.arg_string(arguments)})')
            self.out(f'.def("{pyname}", []({self.arg_string(arguments)})')
            self.out("{")
            ret = "" if self.is_function_void_return(cursor) else "auto ret = "

            result = f"{self.spell(cursor)}({self.arg_names(arguments)})"
            result_type = cursor.result_type
            #logger.debug(f'result_type: {result_type.spelling}')
            result_type_name = result_type.spelling.split(' ')[0]

            if result_type_name in self.wrapped:
                result_type_name = self.wrapped[result_type_name].gen_wrapper['type']
                result = f"new {result_type_name}({result})"

            with self.out:
                self.out(f"{ret}{result};")
                self.out(f"return {self.get_function_result(node, cursor)};")
            self.out("}")
        else:
            #self.out(f'{mname}.def("{pyname}", {cname}')
            self.out(f'.def("{pyname}", {cname}')
        
        with self.out:
            self.write_pyargs(arguments, node)
            #self.out(f", {self.get_return_policy(cursor)});\n")
            self.out(f", {self.get_return_policy(cursor)})")
