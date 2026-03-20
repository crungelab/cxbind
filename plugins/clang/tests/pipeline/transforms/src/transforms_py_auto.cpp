#include <limits>
#include <sstream>

#include <pybind11/pybind11.h>
#include <pybind11/functional.h>
#include <pybind11/stl.h>

#include <cxbind/cxbind.h>
#include "transforms.h"
#include "transforms_2.h"

namespace py = pybind11;

void register_transforms_py_auto(py::module &_tests, Registry &registry) {
    py::class_<Transforms> _Transforms(_tests, "Transforms");
    registry.on(_tests, "Transforms", _Transforms);
        _Transforms
        .def(py::init<int>()
        , py::arg("value") = 0
        )
        .def_readwrite("value", &Transforms::value)
        .def("create_dummy", &transformsCreateDummy
            , py::arg("value")
            , py::return_value_policy::automatic_reference)
    ;

    py::class_<TransformsDummy> _TransformsDummy(_tests, "TransformsDummy");
    registry.on(_tests, "TransformsDummy", _TransformsDummy);
        _TransformsDummy
        .def(py::init<int>()
        , py::arg("value") = 0
        )
        .def_readwrite("value", &TransformsDummy::value)
        .def("__repr__", [](const TransformsDummy &self) {
            std::stringstream ss;
            ss << "TransformsDummy(";
            ss << "value=" << py::repr(py::cast(self.value)).cast<std::string>();
            ss << ")";
            return ss.str();
        })
    ;


}