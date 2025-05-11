#include <limits>

#include <pybind11/pybind11.h>
#include <pybind11/functional.h>
#include <pybind11/stl.h>

#include <cxbind/cxbind.h>
#include "arguments.h"

namespace py = pybind11;

void register_arguments_py_auto(py::module &_core, Registry &registry) {
    py::class_<Arguments> Arguments(_core, "Arguments");
    registry.on(_core, "Arguments", Arguments);
        Arguments
        .def(py::init<>())
        .def("add", &Arguments::add
            , py::arg("i") = 0
            , py::arg("j") = 0
            , py::return_value_policy::automatic_reference)
    ;


}