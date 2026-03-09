#include <limits>

#include <pybind11/pybind11.h>
#include <pybind11/functional.h>
#include <pybind11/stl.h>

#include <cxbind/cxbind.h>
#include "wrappers.h"

namespace py = pybind11;

void register_wrappers_py_auto(py::module &_tests, Registry &registry) {
    _tests
    .def("test_wrapper_in", [](SDLWindowWrapper window, int width, int height)
        {
            return testWrapperIn(static_cast<SDL_Window *>(window.get()), width, height);
        }
        , py::arg("window")
        , py::arg("width")
        , py::arg("height")
        , py::return_value_policy::automatic_reference)
    .def("test_wrapper_out", []()
        {
            return SDLWindowWrapper(testWrapperOut());
        }
        , py::return_value_policy::automatic_reference)
    .def("test_capsule_in", [](py::capsule context, int width, int height)
        {
            return testCapsuleIn(static_cast<ImGuiContext *>(context.get_pointer()), width, height);
        }
        , py::arg("context")
        , py::arg("width")
        , py::arg("height")
        , py::return_value_policy::automatic_reference)
    .def("test_capsule_out", [](int width, int height)
        {
            return py::capsule(testCapsuleOut(width, height), "ImGuiContext");
        }
        , py::arg("width")
        , py::arg("height")
        , py::return_value_policy::automatic_reference)
    ;


}