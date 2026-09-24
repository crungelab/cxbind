import pytest

import cxbind_tests.test_enums as m


# ---------------------------------------------------------------------------
# Basic cases
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "enum_name, members",
    [
        ("SimpleEnum", ["VALUE_1", "VALUE_2", "VALUE_3"]),
        ("ScopedEnum", ["VALUE1", "VALUE2", "VALUE3"]),
        ("RedundantEnum", ["VALUE1", "VALUE2", "VALUE3"]),
        ("NsRedundantEnum", ["VALUE1", "VALUE2", "VALUE3"]),
        ("Enum", ["VALUE1", "VALUE2", "VALUE3"]),
    ],
)
def test_enum_values(enum_name, members):
    enum = getattr(m, enum_name)
    for i, member in enumerate(members):
        assert int(getattr(enum, member)) == i


def test_simple_enum_compares_to_int():
    assert m.SimpleEnum.VALUE_1 == 0


def test_unscoped_constants_exported_to_module():
    assert m.VALUE_1 == m.SimpleEnum.VALUE_1


def test_redundant_prefix_stripped():
    assert not hasattr(m.RedundantEnum, "REDUNDANT_ENUM_VALUE1")
    assert not hasattr(m.NsRedundantEnum, "NS_REDUNDANT_ENUM_VALUE1")


def test_namespace_is_flattened():
    assert hasattr(m, "NsRedundantEnum")
    assert not hasattr(m, "ns")


def test_enum_only_struct_is_flattened():
    # A struct with nothing bindable isn't bound; its enum lands at module scope.
    assert m.Enum.__name__ == "Enum"
    assert not hasattr(m, "EnumStruct")


# ---------------------------------------------------------------------------
# Collision: same name in two flattened namespaces
# ---------------------------------------------------------------------------


def test_namespace_collision_qualifies_both():
    assert m.PrimariesCicpId.__name__ == "PrimariesCicpId"
    assert m.TransferCicpId.__name__ == "TransferCicpId"
    # Neither keeps the bare name, so the result can't depend on declaration order.
    assert not hasattr(m, "CicpId")


def test_qualified_enums_are_distinct_types():
    assert m.PrimariesCicpId is not m.TransferCicpId
    assert type(m.PrimariesCicpId.REC709) is not type(m.TransferCicpId.REC709)


def test_qualified_enums_keep_their_own_members():
    assert int(m.PrimariesCicpId.BT2020) == 9
    assert int(m.TransferCicpId.LINEAR) == 8
    assert not hasattr(m.PrimariesCicpId, "LINEAR")
    assert not hasattr(m.TransferCicpId, "BT2020")


@pytest.mark.parametrize("constant", ["REC709", "UNSPECIFIED", "BT2020", "LINEAR"])
def test_scoped_constants_not_exported(constant):
    # Exporting would silently overwrite one CicpId's constants with the other's.
    assert not hasattr(m, constant)


# ---------------------------------------------------------------------------
# Collision that needs more than one level of qualification
# ---------------------------------------------------------------------------


def test_collision_climbs_until_unique():
    assert m.LeftInnerLevel.__name__ == "LeftInnerLevel"
    assert m.RightInnerLevel.__name__ == "RightInnerLevel"
    for name in ("Level", "InnerLevel"):
        assert not hasattr(m, name)


def test_climbed_enums_keep_their_own_members():
    assert int(m.LeftInnerLevel.HIGH) == 1
    assert int(m.RightInnerLevel.HIGH) == 2
    assert not hasattr(m.LeftInnerLevel, "MID")


# ---------------------------------------------------------------------------
# Same enum name in a bound struct and an enum-only (flattened) struct.
# Widget has a field, so it's bound and Widget::Kind lives inside it.
# Gadget has only the enum, so Gadget::Kind flattens to module scope.
# Different scopes, so no collision and no renames.
# ---------------------------------------------------------------------------


def test_bound_struct_keeps_its_enum():
    assert m.Widget.Kind.__name__ == "Kind"


def test_flattened_struct_enum_lands_at_module_scope():
    assert m.Kind.__name__ == "Kind"
    assert not hasattr(m, "Gadget")


def test_same_name_in_different_scopes_not_renamed():
    assert m.Kind is not m.Widget.Kind
    for name in ("WidgetKind", "GadgetKind"):
        assert not hasattr(m, name)


def test_scoped_by_class_enums_keep_their_own_members():
    assert int(m.Widget.Kind.LARGE) == 1
    assert int(m.Kind.OFF) == 1
    assert not hasattr(m.Widget.Kind, "OFF")
    assert not hasattr(m.Kind, "SMALL")


def test_bound_struct_constants_export_into_class_only():
    assert m.Widget.SMALL == m.Widget.Kind.SMALL
    assert m.Widget.LARGE == m.Widget.Kind.LARGE
    for name in ("SMALL", "LARGE"):
        assert not hasattr(m, name)


def test_flattened_struct_constants_export_to_module():
    assert m.ON == m.Kind.ON
    assert m.OFF == m.Kind.OFF
    assert not hasattr(m.Widget, "ON")