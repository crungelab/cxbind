#include <limits>

#include <pybind11/pybind11.h>
#include <pybind11/functional.h>
#include <pybind11/stl.h>

#include <cxbind/cxbind.h>
#include "arguments.h"

namespace py = pybind11;

void register_arguments_py_auto(py::module &_core, Registry &registry) {
    PYCLASS(_core, Arguments, Arguments)

        .def(py::init<>())

        .def("add", &Arguments::add
            , py::arg("i")
            , py::arg("j")
            , py::return_value_policy::automatic_reference)

        .def("ignore_me", &Arguments::ignore_me
            , py::arg("i")
            , py::arg("j")
            , py::return_value_policy::automatic_reference)
    ;


}