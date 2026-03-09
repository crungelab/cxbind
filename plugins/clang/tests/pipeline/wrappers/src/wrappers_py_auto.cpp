#include <limits>

#include <pybind11/pybind11.h>
#include <pybind11/functional.h>
#include <pybind11/stl.h>

#include <cxbind/cxbind.h>
#include "wrappers.h"

namespace py = pybind11;

void register_wrappers_py_auto(py::module &_tests, Registry &registry) {
    _tests
    .def("wrapper_in_fn", [](SDLWindowWrapper window, int width, int height)
        {
            return wrapperInFn(static_cast<SDL_Window *>(window.get()), width, height);
        }
        , py::arg("window")
        , py::arg("width")
        , py::arg("height")
        , py::return_value_policy::automatic_reference)
    .def("wrapper_out_fn", []()
        {
            return SDLWindowWrapper(wrapperOutFn());
        }
        , py::return_value_policy::automatic_reference)
    .def("capsule_in_fn", [](py::capsule context, int width, int height)
        {
            return capsuleInFn(static_cast<ImGuiContext *>(context.get_pointer()), width, height);
        }
        , py::arg("context")
        , py::arg("width")
        , py::arg("height")
        , py::return_value_policy::automatic_reference)
    .def("capsule_out_fn", [](int width, int height)
        {
            return py::capsule(capsuleOutFn(width, height), "ImGuiContext");
        }
        , py::arg("width")
        , py::arg("height")
        , py::return_value_policy::automatic_reference)
    ;


}