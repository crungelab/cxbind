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
    py::class_<Handle> _Handle(_tests, "Handle");
    registry.on(_tests, "Handle", _Handle);
        _Handle
        .def(py::init<int>()
        , py::arg("value") = 0
        )
        .def_readwrite("value", &Handle::value)
        .def("create_dummy", &CreateDummy)
    ;

    py::class_<Dummy> _Dummy(_tests, "Dummy");
    registry.on(_tests, "Dummy", _Dummy);
        _Dummy
        .def(py::init<int>()
        , py::arg("value") = 0
        )
        .def_readwrite("value", &Dummy::value)
        .def("__repr__", [](const Dummy &self) {
            std::stringstream ss;
            ss << "Dummy(";
            ss << "value=" << py::repr(py::cast(self.value)).cast<std::string>();
            ss << ")";
            return ss.str();
        })
    ;


}