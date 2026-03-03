#include <limits>

#include <pybind11/pybind11.h>
#include <pybind11/functional.h>
#include <pybind11/stl.h>

#include <cxbind/cxbind.h>
#include "arguments.h"

namespace py = pybind11;

void register_arguments_py_auto(py::module &_tests, Registry &registry) {
    py::class_<Arguments> _Arguments(_tests, "Arguments");
    registry.on(_tests, "Arguments", _Arguments);
        _Arguments
        .def(py::init<>())
        .def("add", &Arguments::add
            , py::arg("i")
            , py::arg("j")
            , py::return_value_policy::automatic_reference)
    ;

    _tests
    .def("in_out_function", [](int i, int * j)
        {
            inOutFunction(i, j);
            return std::make_tuple(j);
        }
        , py::arg("i")
        , py::arg("j")
        , py::return_value_policy::automatic_reference)
    ;


}