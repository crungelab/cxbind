#include <limits>

#include <pybind11/pybind11.h>
#include <pybind11/functional.h>
#include <pybind11/stl.h>

#include <cxbind/cxbind.h>
#include "functions.h"

namespace py = pybind11;

void register_functions_py_auto(py::module &_tests, Registry &registry) {
{{body}}
}