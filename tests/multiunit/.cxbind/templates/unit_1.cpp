#include <limits>

#include <pybind11/pybind11.h>
#include <pybind11/functional.h>
#include <pybind11/stl.h>

#include <cxbind/cxbind.h>
#include "unit_1.h"

namespace py = pybind11;

void init_unit_1_py_auto(py::module &_multiunit, Registry &registry) {
{{body}}
}