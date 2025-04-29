#include <pybind11/pybind11.h>

#include <cxbind/cxbind.h>

namespace py = pybind11;

void register_simple_py_auto(py::module &, Registry &registry);
void register_advanced_py_auto(py::module &, Registry &registry);
void register_arguments_py_auto(py::module &, Registry &registry);
void register_enums_py_auto(py::module &, Registry &registry);
void register_exclude_py_auto(py::module &, Registry &registry);
void register_functions_py_auto(py::module &, Registry &registry);
void register_namespace_py_auto(py::module &, Registry &registry);
void register_templates_py_auto(py::module &, Registry &registry);
void register_overloads_py_auto(py::module &, Registry &registry);

void register_unit_1_py_auto(py::module &, Registry &registry);
void register_unit_2_py_auto(py::module &, Registry &registry);


PYBIND11_MODULE(cxbind_tests, m)
{
    Registry r;

    auto _simple = m.def_submodule("test_simple");
    register_simple_py_auto(_simple, r);

    auto _advanced = m.def_submodule("test_advanced");
    register_advanced_py_auto(_advanced, r);

    auto _arguments = m.def_submodule("test_arguments");
    register_arguments_py_auto(_arguments, r);

    auto _enums = m.def_submodule("test_enums");
    register_enums_py_auto(_enums, r);

    auto _exclude = m.def_submodule("test_exclude");
    register_exclude_py_auto(_exclude, r);

    auto _functions = m.def_submodule("test_functions");
    register_functions_py_auto(_functions, r);

    auto _namespace = m.def_submodule("test_namespace");
    register_namespace_py_auto(_namespace, r);

    auto _templates = m.def_submodule("test_templates");
    register_templates_py_auto(_templates, r);

    auto _multiunit = m.def_submodule("test_multiunit");
    register_unit_1_py_auto(_multiunit, r);
    register_unit_2_py_auto(_multiunit, r);

    auto _overloads = m.def_submodule("test_overloads");
    register_overloads_py_auto(_overloads, r);
}