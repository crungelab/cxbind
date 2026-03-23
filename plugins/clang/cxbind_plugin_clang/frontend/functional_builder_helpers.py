from loguru import logger
from clang import cindex

from cxbind.spec import Ownership

FACTORY_PREFIXES = ("Make", "make", "Create", "create", "New", "new")


def looks_like_factory(cursor: cindex.Cursor) -> bool:
    return any(cursor.spelling.startswith(p) for p in FACTORY_PREFIXES)


def parent_owns_return_type(method_cursor: cindex.Cursor) -> bool:
    return_pointee = method_cursor.result_type.get_pointee()
    parent_class = method_cursor.semantic_parent

    for member in parent_class.get_children():
        if member.kind == cindex.CursorKind.FIELD_DECL:
            field_type = member.type.get_canonical()
            if field_type.spelling == return_pointee.spelling:
                return True
            if f"sk_sp<{return_pointee.spelling}>" in field_type.spelling:
                return True
    return False


def infer_ownership(cursor: cindex.Cursor) -> Ownership:
    """
    Returns (Ownership, warning_message).
    warning_message is logged when inference is uncertain.
    """
    rt = cursor.result_type
    canonical = rt.get_canonical()
    method_name = f"{cursor.semantic_parent.spelling}::{cursor.spelling}"

    # sk_sp return — shared/ref-counted, holder manages lifetime
    if rt.spelling.startswith("sk_sp<"):
        return Ownership.SHARED

    # Value type — safe to copy, no RVP needed
    if canonical.kind not in (cindex.TypeKind.POINTER, cindex.TypeKind.LVALUEREFERENCE):
        return Ownership.VALUE

    # rvalue reference — move into Python-owned instance
    if canonical.kind == cindex.TypeKind.RVALUEREFERENCE:
        return Ownership.MOVE

    # From here: pointer or lvalue reference

    # Factory method returning sk_sp — still shared
    if looks_like_factory(cursor) and rt.spelling.startswith("sk_sp<"):
        return Ownership.SHARED

    # Factory method returning raw pointer — likely owned, but warn
    if looks_like_factory(cursor) and canonical.kind == cindex.TypeKind.POINTER:
        logger.warning(f"{method_name} looks like a factory returning a raw pointer; inferring OWNED, but verify manually")
        return Ownership.OWNED

    # Parent class holds a member of the return type — borrowed reference
    if canonical.kind == cindex.TypeKind.POINTER and parent_owns_return_type(cursor):
        return Ownership.BORROWED

    # lvalue reference return — tied to parent lifetime
    if canonical.kind == cindex.TypeKind.LVALUEREFERENCE:
        return Ownership.BORROWED

    # Raw pointer, non-factory, no detected parent ownership —
    # conservative fallback: reference rather than take_ownership
    logger.warning(f"{method_name} returns a raw pointer with no clear ownership; inferring REF, but verify manually")
    return Ownership.REF