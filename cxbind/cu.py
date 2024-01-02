from loguru import logger

from clang import cindex


def print_type_info(node):
    print("Node:", node.spelling)
    print("Node Kind:", node.kind)
    print("Node Parent:", node.semantic_parent.spelling)
    print("Type:", node.type)
    print("Type Kind:", node.type.kind)
    if node.type.kind == cindex.TypeKind.POINTER:
        pointee_type = node.type.get_pointee()
        print("Pointee Type:", pointee_type)
        print("Pointee Type Kind:", pointee_type.kind)

# This was ChatGPT's idea.  Doesn't work.
def find_parent_typedef(cursor):
    # Traverse up the AST from the current cursor and look for a typedef
    parent = cursor.semantic_parent
    while parent is not None:
        if parent.kind == cindex.CursorKind.TYPEDEF_DECL:
            return parent
        parent = parent.semantic_parent
    return None

# This was ChatGPT's idea.  Doesn't work.
def is_template(cursor):
    # Traverse up the AST and check if this is part of a template declaration
    parent = cursor.semantic_parent
    while parent is not None:
        if parent.kind in [cindex.CursorKind.FUNCTION_TEMPLATE,
                           cindex.CursorKind.CLASS_TEMPLATE,
                           cindex.CursorKind.TEMPLATE_TYPE_PARAMETER]:
            return True
        parent = parent.semantic_parent
    return False