#include <limits>

#include <pybind11/pybind11.h>
#include <pybind11/functional.h>
#include <pybind11/stl.h>

#include <cxbind/cxbind.h>
#include "advanced.h"

namespace py = pybind11;

void register_advanced_py_auto(py::module &_core, Registry &registry) {
    _core
    .def("add", &add
        , py::arg("x")
        , py::arg("y")
        , py::return_value_policy::automatic_reference)
    ;

    py::class_<Advanced> Advanced(_core, "Advanced");
    registry.on(_core, "Advanced", Advanced);
        Advanced
        .def(py::init<>())
        .def("add", &Advanced::add
            , py::arg("i")
            , py::arg("j")
            , py::return_value_policy::automatic_reference)
    ;

    _core
    .def("sub", &sub
        , py::arg("x")
        , py::arg("y")
        , py::return_value_policy::automatic_reference)
    ;


}