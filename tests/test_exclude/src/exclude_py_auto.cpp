#include <limits>

#include <pybind11/pybind11.h>
#include <pybind11/functional.h>
#include <pybind11/stl.h>

#include <cxbind/cxbind.h>
#include "exclude.h"

namespace py = pybind11;

void register_exclude_py_auto(py::module &_core, Registry &registry) {
    py::class_<Exclude> Exclude(_core, "Exclude");
    registry.on(_core, "Exclude", Exclude);
        Exclude
        .def(py::init<>())
        .def("add", &Exclude::add
            , py::arg("i")
            , py::arg("j")
            , py::return_value_policy::automatic_reference)
        .def("sub", &Exclude::sub
            , py::arg("i")
            , py::arg("j")
            , py::return_value_policy::automatic_reference)
    ;


}