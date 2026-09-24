import inspect

import pytest

import cxbind_tests.test_methods as m
from cxbind_tests.test_methods import Methods


def is_static(name: str) -> bool:
    # def_static stores a staticmethod on the class; def stores an instance method.
    return isinstance(inspect.getattr_static(Methods, name), staticmethod)


# ---------------------------------------------------------------------------
# Basic cases
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "value, arg, expected",
    [
        (2, 2, 4),
        (2, 4, 6),
        (0, 5, 5),
        (-3, 3, 0),
    ],
)
def test_add(value, arg, expected):
    assert Methods(value).add(arg) == expected


def test_excluded_method_not_exposed():
    assert not hasattr(Methods, "ignore_me")


# ---------------------------------------------------------------------------
# Static/instance collision
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("name", ["equals", "compare", "scale"])
def test_collision_resolved_regardless_of_declaration_order(name):
    # Instance keeps the bare name, static gets the suffix, whichever came first.
    assert not is_static(name)
    assert is_static(f"{name}_static")


@pytest.mark.parametrize("name", ["Equals", "Compare", "Scale", "equals_static_static"])
def test_no_stray_names(name):
    assert not hasattr(Methods, name)


def test_statics_not_hoisted_to_module():
    for name in ("equals", "equals_static", "compare", "compare_static", "scale", "scale_static"):
        assert not hasattr(m, name)


def test_instance_equals():
    assert Methods(1).equals(Methods(1))
    assert not Methods(1).equals(Methods(2))


def test_static_equals():
    assert Methods.equals_static(Methods(1), Methods(1))
    assert not Methods.equals_static(Methods(1), Methods(2))


def test_static_callable_through_instance():
    a = Methods(1)
    assert a.equals_static(a, Methods(1))


def test_class_level_call_is_unbound_instance_method():
    # Without a hybrid descriptor, Methods.equals(a, b) means a.equals(b).
    assert Methods.equals(Methods(3), Methods(3))


@pytest.mark.parametrize(
    "a, b, expected",
    [
        (1, 2, -1),
        (2, 2, 0),
        (3, 2, 1),
    ],
)
def test_compare_instance_and_static_agree(a, b, expected):
    assert Methods(a).compare(Methods(b)) == expected
    assert Methods.compare_static(Methods(a), Methods(b)) == expected


# ---------------------------------------------------------------------------
# Static/instance collision where the static is a C++ overload set
# ---------------------------------------------------------------------------


def test_instance_scale():
    assert Methods(2).scale(3) == 6


@pytest.mark.parametrize(
    "args, expected",
    [
        ((3,), 6),
        ((3, 1), 7),
    ],
)
def test_static_scale_overloads(args, expected):
    assert Methods.scale_static(Methods(2), *args) == expected


def test_static_overloads_stay_one_overload_set():
    # Both overloads were renamed together rather than qualified apart.
    assert "Overloaded function" in Methods.scale_static.__doc__


def test_instance_scale_is_not_an_overload_set():
    assert "Overloaded function" not in (Methods.scale.__doc__ or "")


# ---------------------------------------------------------------------------
# Static without a collision
# ---------------------------------------------------------------------------


def test_non_colliding_static_keeps_name():
    assert is_static("make")
    assert not hasattr(Methods, "make_static")
    assert Methods.make(5).add(0) == 5