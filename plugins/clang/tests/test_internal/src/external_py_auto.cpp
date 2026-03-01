#include <limits>
#include <sstream>

#include <pybind11/pybind11.h>
#include <pybind11/functional.h>
#include <pybind11/stl.h>

#include <cxbind/cxbind.h>
#include "external.h"
#include "internal.h"

namespace py = pybind11;

void register_internal_py_auto(py::module &_tests, Registry &registry) {
    py::class_<Internal> _Internal(_tests, "Internal");
    registry.on(_tests, "Internal", _Internal);
        _Internal
        .def(py::init<int>()
        , py::arg("value") = 0
        )
        .def_readwrite("value", &Internal::value)
        .def("create_dummy", &CreateDummy)
    ;

    py::class_<InternalDummy> _InternalDummy(_tests, "InternalDummy");
    registry.on(_tests, "InternalDummy", _InternalDummy);
        _InternalDummy
        .def(py::init<int>()
        , py::arg("value") = 0
        )
        .def_readwrite("value", &InternalDummy::value)
        .def("__repr__", [](const InternalDummy &self) {
            std::stringstream ss;
            ss << "InternalDummy(";
            ss << "value=" << py::repr(py::cast(self.value)).cast<std::string>();
            ss << ")";
            return ss.str();
        })
    ;


}