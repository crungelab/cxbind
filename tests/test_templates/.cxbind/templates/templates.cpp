#include <limits>

#include <pybind11/pybind11.h>
#include <pybind11/functional.h>
#include <pybind11/stl.h>

#include <cxbind/cxbind.h>
#include "templates.h"

namespace py = pybind11;

void register_templates_py_auto(py::module &_core, Registry &registry) {
{{body}}
}