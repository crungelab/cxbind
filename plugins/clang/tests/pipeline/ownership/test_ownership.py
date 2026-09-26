"""Ownership: observed through C++ instance counters, not generated text.

Each test checks what actually happens to the C++ object when Python
references, copies, owns or releases it.
"""

import gc
import unittest

import cxbind_tests.test_ownership as m


def collect() -> None:
    gc.collect()


class TestInferred(unittest.TestCase):
    """No spec: ownership comes from the return type's kind."""

    def test_reference_return_writes_through(self):
        widget = m.get_widget_ref()
        widget.value = 42
        self.assertEqual(m.get_widget_ref_value(), 42)

    def test_pointer_return_is_not_deleted(self):
        m.get_widget_ptr()  # construct the static first
        collect()
        before = m.live_widgets()

        widget = m.get_widget_ptr()
        del widget
        collect()
        self.assertEqual(m.live_widgets(), before)

    def test_value_return_is_a_python_owned_copy(self):
        collect()
        before = m.live_widgets()

        widget = m.make_widget()
        self.assertEqual(widget.value, 7)
        self.assertEqual(m.live_widgets(), before + 1)

        del widget
        collect()
        self.assertEqual(m.live_widgets(), before)


class TestExplicitFunction(unittest.TestCase):
    def test_owned_return_is_deleted_by_python(self):
        collect()
        before = m.live_widgets()

        widget = m.create_widget()
        self.assertEqual(m.live_widgets(), before + 1)

        del widget
        collect()
        self.assertEqual(m.live_widgets(), before)


class TestSpecWithoutOwnership(unittest.TestCase):
    """Regression: a type spec that doesn't set ownership must not disable inference."""

    def test_reference_return_writes_through(self):
        settings = m.get_settings()
        settings.level = 3
        self.assertEqual(m.get_settings_level(), 3)

    def test_pointer_return_writes_through(self):
        settings = m.get_settings_ptr()
        settings.level = 9
        self.assertEqual(m.get_settings_level(), 9)


class TestExplicitType(unittest.TestCase):
    def test_type_ownership_applies(self):
        collect()
        before = m.live_handles()

        handle = m.new_handle()
        self.assertEqual(m.live_handles(), before + 1)

        del handle
        collect()
        self.assertEqual(m.live_handles(), before)

    def test_function_spec_overrides_type(self):
        m.peek_handle()  # construct the static first
        collect()
        before = m.live_handles()

        handle = m.peek_handle()
        del handle
        collect()
        self.assertEqual(m.live_handles(), before)


class TestBorrowed(unittest.TestCase):
    def test_child_keeps_parent_alive(self):
        collect()
        before = m.live_parents()

        parent = m.Parent()
        child = parent.get_child()
        del parent
        collect()
        # reference_internal: the child keeps its parent alive...
        self.assertEqual(m.live_parents(), before + 1)
        self.assertEqual(child.value, 5)

        del child
        collect()
        # ...until the child itself is released.
        self.assertEqual(m.live_parents(), before)


if __name__ == "__main__":
    unittest.main()