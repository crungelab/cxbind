#include <limits>

#include <pybind11/pybind11.h>
#include <pybind11/functional.h>
#include <pybind11/stl.h>

#include <cxbind/cxbind.h>
#include "aliases.h"

namespace py = pybind11;

using AliasClassI = AliasClass<int>;

using IntAddPtr = int (*)(int, int); 
IntAddPtr aliasFunctionI = &aliasFunction<int>;

void register_aliases_py_auto(py::module &_tests, Registry &registry) {
    py::class_<AliasClassI> _AliasClassI(_tests, "AliasClassI");
    registry.on(_tests, "AliasClassI", _AliasClassI);
        _AliasClassI
        .def(py::init<int>()
        , py::arg("value")
        )
        .def("set_value", &AliasClassI::setValue
            , py::arg("value")
            , py::return_value_policy::automatic_reference)
        .def("get_value", &AliasClassI::getValue
            , py::return_value_policy::automatic_reference)
    ;

    _tests
    .def("alias_function_float", &aliasFunction<float>
        , py::return_value_policy::automatic_reference)
    .def("alias_function_i", aliasFunctionI
        , py::return_value_policy::automatic_reference)
    ;


}