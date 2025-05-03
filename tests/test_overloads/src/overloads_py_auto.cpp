#include <limits>

#include <pybind11/pybind11.h>
#include <pybind11/functional.h>
#include <pybind11/stl.h>

#include <cxbind/cxbind.h>
#include "overloads.h"

namespace py = pybind11;

void register_overloads_py_auto(py::module &_core, Registry &registry) {
    py::class_<Overloads> Overloads(_core, "Overloads");
    registry.on(_core, "Overloads", Overloads);
        Overloads
        .def(py::init<>())
        .def("add", py::overload_cast<int, int>(&Overloads::add)
            , py::arg("i")
            , py::arg("j")
            , py::return_value_policy::automatic_reference)
        .def("add", py::overload_cast<float, float>(&Overloads::add)
            , py::arg("i")
            , py::arg("j")
            , py::return_value_policy::automatic_reference)
    ;


}