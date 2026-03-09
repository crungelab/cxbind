#include <limits>
#include <sstream>

#include <pybind11/pybind11.h>
#include <pybind11/functional.h>
#include <pybind11/stl.h>

#include <cxbind/cxbind.h>
#include "handles.h"

namespace py = pybind11;

void register_handles_py_auto(py::module &_tests, Registry &registry) {
    py::class_<Handle> _Handle(_tests, "Handle");
    registry.on(_tests, "Handle", _Handle);
        _Handle
        .def(py::init<int>()
        , py::arg("value") = 0
        )
        .def_readwrite("value", &Handle::value)
        .def("create_dummy", &handleCreateDummy)
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

    _tests
    .def("handle_create_dummy", &handleCreateDummy
        , py::arg("handle")
        , py::arg("value")
        , py::return_value_policy::automatic_reference)
    ;


}