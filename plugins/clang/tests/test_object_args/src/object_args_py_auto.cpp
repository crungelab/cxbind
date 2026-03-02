#include <limits>

#include <pybind11/pybind11.h>
#include <pybind11/functional.h>
#include <pybind11/stl.h>

#include <cxbind/cxbind.h>
#include "object_args.h"

namespace py = pybind11;

void register_object_args_py_auto(py::module &_tests, Registry &registry) {
    _tests
    .def("function_with_void_arg", [](py::object obj)
        {
            functionWithVoidArg(static_cast<void *>(obj.ptr()));
            return ;
        }
        , py::arg("obj")
        , py::return_value_policy::automatic_reference)
    ;


}