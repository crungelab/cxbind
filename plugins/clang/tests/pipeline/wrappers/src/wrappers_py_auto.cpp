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
        )
    .def("wrapper_out_fn", []()
        {
            return SDLWindowWrapper(wrapperOutFn());
        }
        )
    .def("capsule_in_fn", [](py::capsule context, int width, int height)
        {
            return capsuleInFn(static_cast<ImGuiContext *>(context.get_pointer()), width, height);
        }
        , py::arg("context")
        , py::arg("width")
        , py::arg("height")
        )
    .def("capsule_out_fn", [](int width, int height)
        {
            return py::capsule(capsuleOutFn(width, height), "ImGuiContext");
        }
        , py::arg("width")
        , py::arg("height")
        )
    ;

    py::class_<WrapperStruct> _WrapperStruct(_tests, "WrapperStruct");
    registry.on(_tests, "WrapperStruct", _WrapperStruct);
        _WrapperStruct
        //render_pycapsule_field
        .def_property("context",
            [](const WrapperStruct& self){ return py::capsule(self.context, "ImGuiContext"); },
            [](WrapperStruct& self, const py::capsule& value){ self.context = value; }
        )
        //render_wrapper_field
        .def_property("window",
            [](const WrapperStruct& self){ return SDLWindowWrapper(self.window); },
            [](WrapperStruct& self, const SDLWindowWrapper& value){ self.window = value; }
        )
    ;


}