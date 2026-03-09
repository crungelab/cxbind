#include <limits>

#include <pybind11/pybind11.h>
#include <pybind11/functional.h>
#include <pybind11/stl.h>

#include <cxbind/cxbind.h>
#include "overloads.h"

namespace py = pybind11;

void register_overloads_py_auto(py::module &_tests, Registry &registry) {
    py::class_<OtherClass> _OtherClass(_tests, "OtherClass");
    registry.on(_tests, "OtherClass", _OtherClass);
        _OtherClass
        .def_readwrite("i", &OtherClass::i)
        .def_readwrite("j", &OtherClass::j)
    ;

    py::class_<Overloads> _Overloads(_tests, "Overloads");
    registry.on(_tests, "Overloads", _Overloads);
        _Overloads
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