#include <limits>

#include <pybind11/pybind11.h>
#include <pybind11/functional.h>
#include <pybind11/stl.h>

#include <cxbind/cxbind.h>

#include "methods.h"

namespace py = pybind11;

void register_methods_py_auto(py::module &_tests, Registry &registry) {
    py::class_<Methods> _Methods(_tests, "Methods");
    registry.on(_tests, "Methods", _Methods);
        _Methods
        .def(py::init<int>()
        , py::arg("value") = 0
        )
        .def("add", &Methods::add
            , py::arg("i")
            )
        .def("equals", &Methods::equals
            , py::arg("other")
            )
        .def_static("equals_static", &Methods::Equals
            , py::arg("a")
            , py::arg("b")
            )
        .def_static("compare_static", &Methods::Compare
            , py::arg("a")
            , py::arg("b")
            )
        .def("compare", &Methods::compare
            , py::arg("other")
            )
        .def("scale", &Methods::scale
            , py::arg("factor")
            )
        .def_static("scale_static", py::overload_cast<const Methods &, int>(&Methods::Scale)
            , py::arg("m")
            , py::arg("factor")
            )
        .def_static("scale_static", py::overload_cast<const Methods &, int, int>(&Methods::Scale)
            , py::arg("m")
            , py::arg("factor")
            , py::arg("offset")
            )
        .def_static("make", &Methods::Make
            , py::arg("value")
            )
        .def_readwrite("value", &Methods::value)
    ;


}
