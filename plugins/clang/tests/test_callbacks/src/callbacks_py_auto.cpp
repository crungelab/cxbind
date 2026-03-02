#include <limits>

#include <pybind11/pybind11.h>
#include <pybind11/functional.h>
#include <pybind11/stl.h>

#include <cxbind/cxbind.h>
#include "callbacks.h"

namespace py = pybind11;

void register_callbacks_py_auto(py::module &_tests, Registry &registry) {
    _tests
    .def("callback", &callback
        , py::arg("value")
        , py::return_value_policy::automatic_reference)
    .def("function_with_callback", [](std::vector<unsigned int> a, bool (int) callback)
        {
            const uint32_t * _a = (const uint32_t *)a.data();
            auto count = a.size();
            
            functionWithCallback(_a, count, callback);
            return ;
        }
        , py::arg("a")
        , py::arg("callback")
        , py::return_value_policy::automatic_reference)
    ;


}