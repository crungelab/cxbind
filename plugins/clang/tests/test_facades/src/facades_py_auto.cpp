#include <limits>

#include <pybind11/pybind11.h>
#include <pybind11/functional.h>
#include <pybind11/stl.h>

#include <cxbind/cxbind.h>
#include "facades.h"

namespace py = pybind11;

void register_facades_py_auto(py::module &_tests, Registry &registry) {
    _tests
    .def("facade_function", [](std::vector<unsigned int> a)
        {
            const uint32_t * _a = (const uint32_t *)a.data();
            auto count = a.size();
            
            auto ret = facadeFunction(_a, count);
            return ret;
        }
        , py::arg("a")
        , py::return_value_policy::automatic_reference)
    ;


}