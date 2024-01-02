from clang import cindex

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
    cindex.CursorKind.TYPEDEF_DECL : lambda self, node : self.visit_typedef_decl(node),

    cindex.CursorKind.FUNCTION_TEMPLATE : lambda self, node : self.visit_none(node),
    cindex.CursorKind.CLASS_TEMPLATE : lambda self, node : self.visit_none(node),
    cindex.CursorKind.CLASS_TEMPLATE_PARTIAL_SPECIALIZATION : lambda self, node : self.visit_none(node),
    cindex.CursorKind.TYPE_ALIAS_TEMPLATE_DECL : lambda self, node : self.visit_none(node),
    cindex.CursorKind.TEMPLATE_REF : lambda self, node : self.visit_none(node),
}

'''
        if parent.kind in [cindex.CursorKind.FUNCTION_TEMPLATE,
                           cindex.CursorKind.CLASS_TEMPLATE,
                           cindex.CursorKind.TEMPLATE_TYPE_PARAMETER]:
            return True
'''