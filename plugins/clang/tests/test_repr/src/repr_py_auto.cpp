#include <limits>

#include <pybind11/pybind11.h>
#include <pybind11/functional.h>
#include <pybind11/stl.h>

#include <cxbind/cxbind.h>
#include "repr.h"

namespace py = pybind11;

void register_repr_py_auto(py::module &_tests, Registry &registry) {
    py::class_<Repr> _Repr(_tests, "Repr");
    registry.on(_tests, "Repr", _Repr);
        _Repr
        .def(py::init<int>()
        , py::arg("value") = 0
        )
        .def("add", &Repr::add
            , py::arg("i")
            , py::return_value_policy::automatic_reference)
        .def_readwrite("value", &Repr::value)
    ;


}