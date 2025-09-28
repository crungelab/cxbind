#include <limits>

#include <pybind11/pybind11.h>
#include <pybind11/functional.h>
#include <pybind11/stl.h>

#include <cxbind/cxbind.h>
#include "aliases.h"

namespace py = pybind11;

void register_aliases_py_auto(py::module &_tests, Registry &registry) {
    _tests
    .def("facade_function", [](unsigned int count, int * a)
        {
            auto ret = facadeFunction(count, a);
            return std::make_tuple(ret, a);
        }
        , py::arg("count")
        , py::arg("a")
        , py::return_value_policy::automatic_reference)
    ;


}