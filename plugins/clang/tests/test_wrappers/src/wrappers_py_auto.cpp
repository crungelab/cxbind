#include <limits>

#include <pybind11/pybind11.h>
#include <pybind11/functional.h>
#include <pybind11/stl.h>

#include <cxbind/cxbind.h>
#include "wrappers.h"

namespace py = pybind11;

void register_wrappers_py_auto(py::module &_tests, Registry &registry) {
    _tests
    .def("test_wrapper_in", [](SDL_Window * window, int width, int height)
        {
            return testWrapperIn(window, width, height);
        }
        , py::arg("window")
        , py::arg("width")
        , py::arg("height")
        , py::return_value_policy::automatic_reference)
    .def("test_wrapper_out", []()
        {
            return testWrapperOut();
        }
        , py::return_value_policy::automatic_reference)
    .def("test_capsule_in", [](ImGuiContext * context, int width, int height)
        {
            return testCapsuleIn(context, width, height);
        }
        , py::arg("context")
        , py::arg("width")
        , py::arg("height")
        , py::return_value_policy::automatic_reference)
    .def("test_capsule_out", [](int width, int height)
        {
            return testCapsuleOut(width, height);
        }
        , py::arg("width")
        , py::arg("height")
        , py::return_value_policy::automatic_reference)
    ;


}