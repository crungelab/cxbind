#include <limits>

#include <pybind11/pybind11.h>
#include <pybind11/functional.h>
#include <pybind11/stl.h>

#include <cxbind/cxbind.h>
#include <cxbind/callback.h>

#include "callbacks.h"

namespace py = pybind11;

void register_callbacks_py_auto(py::module &_tests, Registry &registry) {
    _tests
    .def("function_with_callback", [](std::vector<unsigned int> a, py::function cb)
        {
            const uint32_t * _a = (const uint32_t *)a.data();
            auto count = a.size();
            
            cxbind::thunk_state _context(cb);
            auto context = &_context;
            auto _cb = +[](int value, void * context) -> bool {
                auto& ts = *static_cast<cxbind::thunk_state*>(context);
                // ... use ts, acquire GIL, call Python, etc ...
                py::gil_scoped_acquire gil;
                py::object result = ts.cb(value);
                return result.cast<bool>();
            };
            
            return functionWithCallback(_a, count, _cb, context);
        }
        , py::arg("a")
        , py::arg("cb")
        )
    .def("function_with_callback2", [](std::vector<unsigned int> a, py::function cb)
        {
            const uint32_t * _a = (const uint32_t *)a.data();
            auto count = a.size();
            
            cxbind::thunk_state _context(cb);
            auto context = &_context;
            auto _cb = +[](int value, void * context) -> bool {
                auto& ts = *static_cast<cxbind::thunk_state*>(context);
                // ... use ts, acquire GIL, call Python, etc ...
                py::gil_scoped_acquire gil;
                py::object result = ts.cb(value);
                return result.cast<bool>();
            };
            
            return functionWithCallback2(_a, count, _cb, context);
        }
        , py::arg("a")
        , py::arg("cb")
        )
    .def("function_with_callback_signature", &functionWithCallbackSignature
        , py::arg("a")
        , py::arg("count")
        , py::arg("cb") = nullptr
        , py::arg("context")
        )
    ;


}