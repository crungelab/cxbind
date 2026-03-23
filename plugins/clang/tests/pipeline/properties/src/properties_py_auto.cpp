#include <limits>

#include <pybind11/pybind11.h>
#include <pybind11/functional.h>
#include <pybind11/stl.h>

#include <cxbind/cxbind.h>
#include "properties.h"

namespace py = pybind11;

void register_properties_py_auto(py::module &_tests, Registry &registry) {
    py::class_<Properties> _Properties(_tests, "Properties");
    registry.on(_tests, "Properties", _Properties);
        _Properties
        .def(py::init<>())
        .def("get_x", &Properties::getX
            )
        .def("set_x", &Properties::setX
            , py::arg("value")
            )
        .def("get_y", &Properties::getY
            )
        .def("add", &Properties::add
            , py::arg("i")
            , py::arg("j")
            )
        .def_readwrite("x", &Properties::x)
        .def_property("x", &Properties::getX, &Properties::setX)
        .def_property_readonly("y", &Properties::getY)
    ;


}