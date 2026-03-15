from loguru import logger

from clang import cindex


def print_type_info(cursor) -> None:
    print("Node:", cursor.spelling)
    print("Node Kind:", cursor.kind)
    print("Node Parent:", cursor.semantic_parent.spelling)
    print("Type:", cursor.type)
    print("Type Kind:", cursor.type.kind)
    if cursor.type.kind == cindex.TypeKind.POINTER:
        pointee_type = cursor.type.get_pointee()
        print("Pointee Type:", pointee_type)
        print("Pointee Type Kind:", pointee_type.kind)


def is_template(cursor: cindex.Cursor) -> bool:
    if cursor.get_canonical().kind in [
        cindex.CursorKind.FUNCTION_TEMPLATE,
        cindex.CursorKind.CLASS_TEMPLATE,
        cindex.CursorKind.TEMPLATE_TYPE_PARAMETER,
    ]:
        return True
    return False

# TODO: Skipping anonymous structs for now.
def anonymous_struct_name(anon_struct_cursor: cindex.Cursor) -> str | None:
    """
    Given a CursorKind.STRUCT_DECL cursor with no spelling (anonymous),
    return the field name that names this anonymous struct as a member.
    For: `struct { ... } indices;`  ->  "indices"
    """
    # Usually the semantic_parent is the containing record/class
    parent = anon_struct_cursor.semantic_parent or anon_struct_cursor.lexical_parent
    if not parent:
        return None

    for child in parent.get_children():
        if child.kind == cindex.CursorKind.FIELD_DECL:
            # For a field like: `struct { ... } indices;`
            # child.type.get_declaration() points to the anonymous STRUCT_DECL
            decl = child.type.get_declaration()
            if decl and decl == anon_struct_cursor:
                return child.spelling
    return None
