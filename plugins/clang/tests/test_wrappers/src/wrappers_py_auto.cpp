#include <limits>

#include <pybind11/pybind11.h>
#include <pybind11/functional.h>
#include <pybind11/stl.h>

#include <cxbind/cxbind.h>
#include "wrappers.h"

namespace py = pybind11;

void register_wrappers_py_auto(py::module &_tests, Registry &registry) {
    _tests
    .def("test_wrapper", [](const SDLWindowWrapper& window, int width, int height)
        {
            return testWrapper(window.get(), width, height);
        }
        , py::arg("window")
        , py::arg("width")
        , py::arg("height")
        , py::return_value_policy::automatic_reference)
    .def("return_window", []()
        {
            return SDLWindowWrapper(returnWindow());
        }
        , py::return_value_policy::automatic_reference)
    ;


}