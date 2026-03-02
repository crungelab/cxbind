#include <limits>

#include <pybind11/pybind11.h>
#include <pybind11/functional.h>
#include <pybind11/stl.h>

#include <cxbind/cxbind.h>
#include "callbacks.h"

namespace py = pybind11;

void register_callbacks_py_auto(py::module &_tests, Registry &registry) {
    _tests
    .def("function_with_callback", [](std::vector<unsigned int> a, py::function callback, void * context)
        {
            const uint32_t * _a = (const uint32_t *)a.data();
            auto count = a.size();
            
            auto _callback = +[](b2ShapeId shapeId, void* ctx) -> bool {
                auto* st = static_cast<OverlapThunkState*>(ctx);
                // ... use st, acquire GIL, call Python, etc ...
                return true;
            };
            
            functionWithCallback(_a, count, _callback, context);
            return ;
        }
        , py::arg("a")
        , py::arg("callback")
        , py::arg("context")
        , py::return_value_policy::automatic_reference)
    ;


}