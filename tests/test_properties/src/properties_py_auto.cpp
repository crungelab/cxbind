#include <limits>

#include <pybind11/pybind11.h>
#include <pybind11/functional.h>
#include <pybind11/stl.h>

#include <cxbind/cxbind.h>
#include "properties.h"

namespace py = pybind11;

void register_properties_py_auto(py::module &_core, Registry &registry) {
    py::class_<Properties> Properties(_core, "Properties");
    registry.on(_core, "Properties", Properties);
        Properties
        .def(py::init<>())
        .def("get_x", &Properties::getX
            , py::return_value_policy::automatic_reference)
        .def("set_x", &Properties::setX
            , py::arg("value")
            , py::return_value_policy::automatic_reference)
        .def("get_y", &Properties::getY
            , py::return_value_policy::automatic_reference)
        .def("add", &Properties::add
            , py::arg("i")
            , py::arg("j")
            , py::return_value_policy::automatic_reference)
        .def_readwrite("x", &Properties::x)
        .def_property("x", &Properties::getX, &Properties::setX)
        .def_property_readonly("y", &Properties::getY)
    ;


}