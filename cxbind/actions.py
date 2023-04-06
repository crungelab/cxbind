#from clang import cindex
#from .clang import cindex # Won't work because we're using importlib to import this module
from cxbind.clang import cindex

MAP = {
    cindex.CursorKind.STRUCT_DECL : lambda self, node : self.visit_struct(node),
    cindex.CursorKind.CLASS_DECL : lambda self, node : self.visit_class(node),
    cindex.CursorKind.ENUM_DECL : lambda self, node : self.visit_enum(node),
    cindex.CursorKind.FIELD_DECL : lambda self, node : self.visit_field(node),
    cindex.CursorKind.VAR_DECL : lambda self, node : self.visit_var(node),
    cindex.CursorKind.FUNCTION_DECL : lambda self, node : self.visit_function(node),
    cindex.CursorKind.CXX_METHOD : lambda self, node : self.visit_method(node),
    cindex.CursorKind.CONSTRUCTOR : lambda self, node : self.visit_constructor(node),
    cindex.CursorKind.NAMESPACE : lambda self, node : self.visit_children(node),
    cindex.CursorKind.UNEXPOSED_DECL : lambda self, node : self.visit_children(node),
    cindex.CursorKind.USING_DECLARATION : lambda self, node : self.visit_using_decl(node),
}