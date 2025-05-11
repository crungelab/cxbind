#include <limits>

#include <pybind11/pybind11.h>
#include <pybind11/functional.h>
#include <pybind11/stl.h>

#include <cxbind/cxbind.h>
#include "namespace.h"

namespace py = pybind11;

void register_namespace_py_auto(py::module &_core, Registry &registry) {
    py::class_<ns1::Ns1> Ns1(_core, "Ns1");
    registry.on(_core, "Ns1", Ns1);
        Ns1
        .def(py::init<>())
        .def("add", &ns1::Ns1::add
            , py::arg("i")
            , py::arg("j")
            , py::return_value_policy::automatic_reference)
    ;

    py::class_<ns2::Ns2> Ns2(_core, "Ns2");
    registry.on(_core, "Ns2", Ns2);
        Ns2
        .def(py::init<>())
        .def("add", py::overload_cast<int, int>(&ns2::Ns2::add)
            , py::arg("i")
            , py::arg("j")
            , py::return_value_policy::automatic_reference)
        .def("add", py::overload_cast<ns1::Ns1>(&ns2::Ns2::add)
            , py::arg("other")
            , py::return_value_policy::automatic_reference)
    ;


}