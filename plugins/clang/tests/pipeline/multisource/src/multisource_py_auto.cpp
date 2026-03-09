#include <limits>

#include <pybind11/pybind11.h>
#include <pybind11/functional.h>
#include <pybind11/stl.h>

#include <cxbind/cxbind.h>
#include "multisource_1.h"
#include "multisource_2.h"

namespace py = pybind11;

void register_multisource_py_auto(py::module &_tests, Registry &registry) {
    py::class_<Multisource1> _Multisource1(_tests, "Multisource1");
    registry.on(_tests, "Multisource1", _Multisource1);
        _Multisource1
        .def(py::init<>())
        .def("add", &Multisource1::add
            , py::arg("i")
            , py::arg("j")
            , py::return_value_policy::automatic_reference)
    ;


    py::class_<Multisource2> _Multisource2(_tests, "Multisource2");
    registry.on(_tests, "Multisource2", _Multisource2);
        _Multisource2
        .def(py::init<>())
        .def("add", &Multisource2::add
            , py::arg("i")
            , py::arg("j")
            , py::return_value_policy::automatic_reference)
    ;


}