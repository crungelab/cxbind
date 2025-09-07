from loguru import logger

from clang import cindex


def print_type_info(node) -> None:
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
def find_parent_typedef(cursor: cindex.Cursor) -> cindex.Cursor:
    # Traverse up the AST from the current cursor and look for a typedef
    parent = cursor.semantic_parent
    while parent is not None:
        if parent.kind == cindex.CursorKind.TYPEDEF_DECL:
            return parent
        parent = parent.semantic_parent
    return None


def is_template(cursor: cindex.Cursor) -> bool:
    if cursor.get_canonical().kind in [
        cindex.CursorKind.FUNCTION_TEMPLATE,
        cindex.CursorKind.CLASS_TEMPLATE,
        cindex.CursorKind.TEMPLATE_TYPE_PARAMETER,
    ]:
        return True
    return False


# Function to get the base type name without qualifiers or pointers
def get_base_type_name(typ):
    # Loop to remove qualifiers like 'const' or 'volatile' and dereference pointers/references
    while True:
        # Remove const/volatile qualifiers
        if typ.is_const_qualified() or typ.is_volatile_qualified():
            typ = typ.get_canonical()

        # If the type is a pointer or reference, dereference it
        if typ.kind == cindex.TypeKind.POINTER:
            typ = typ.get_pointee()
        elif (
            typ.kind == cindex.TypeKind.LVALUEREFERENCE
            or typ.kind == cindex.TypeKind.RVALUEREFERENCE
        ):
            typ = typ.get_pointee()
        else:
            # When no more qualifiers or pointers, break out of the loop
            break

    # Return the base type name
    # return typ.spelling
    return typ.spelling.replace("const ", "").replace("volatile ", "")
