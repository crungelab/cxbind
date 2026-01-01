#include <limits>

#include <pybind11/pybind11.h>
#include <pybind11/functional.h>
#include <pybind11/stl.h>

#include <cxbind/cxbind.h>
#include "advanced.h"

namespace py = pybind11;

void register_advanced_py_auto(py::module &_tests, Registry &registry) {
    py::class_<Advanced> _Advanced(_tests, "Advanced");
    registry.on(_tests, "Advanced", _Advanced);
        _Advanced
        .def(py::init<int>()
        , py::arg("value") = 0
        )
        .def("add", &Advanced::add
            , py::arg("i")
            , py::return_value_policy::automatic_reference)
        .def("ignore_me", &Advanced::ignore_me
            , py::arg("i")
            , py::return_value_policy::automatic_reference)
        .def_readwrite("value", &Advanced::value)
    ;


}