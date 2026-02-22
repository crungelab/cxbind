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
void register_inits_py_auto(py::module &, Registry &registry);
void register_templates_py_auto(py::module &, Registry &registry);
void register_aliases_py_auto(py::module &, Registry &registry);
void register_overloads_py_auto(py::module &, Registry &registry);
void register_defaults_py_auto(py::module &, Registry &registry);
void register_multisource_py_auto(py::module &, Registry &registry);
void register_properties_py_auto(py::module &, Registry &registry);
void register_bitfields_py_auto(py::module &, Registry &registry);

void register_unit_1_py_auto(py::module &, Registry &registry);
void register_unit_2_py_auto(py::module &, Registry &registry);

void register_repr_py_auto(py::module &, Registry &registry);
void register_handles_py_auto(py::module &, Registry &registry);

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

    auto _aliases = m.def_submodule("test_aliases");
    register_aliases_py_auto(_aliases, r);

    auto _multiunit = m.def_submodule("test_multiunit");
    register_unit_1_py_auto(_multiunit, r);
    register_unit_2_py_auto(_multiunit, r);

    auto _overloads = m.def_submodule("test_overloads");
    register_overloads_py_auto(_overloads, r);

    auto _defaults = m.def_submodule("test_defaults");
    register_defaults_py_auto(_defaults, r);

    auto _inits = m.def_submodule("test_inits");
    register_inits_py_auto(_inits, r);

    auto _multisource = m.def_submodule("test_multisource");
    register_multisource_py_auto(_multisource, r);

    auto _properties = m.def_submodule("test_properties");
    register_properties_py_auto(_properties, r);

    auto _bitfields = m.def_submodule("test_bitfields");
    register_bitfields_py_auto(_bitfields, r);

    auto _repr = m.def_submodule("test_repr");
    register_repr_py_auto(_repr, r);

    auto _handles = m.def_submodule("test_handles");
    register_handles_py_auto(_handles, r);
}