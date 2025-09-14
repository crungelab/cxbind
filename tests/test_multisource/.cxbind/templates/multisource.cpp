#include <limits>

#include <pybind11/pybind11.h>
#include <pybind11/functional.h>
#include <pybind11/stl.h>

#include <cxbind/cxbind.h>
#include "multisource_1.h"
#include "multisource_2.h"

namespace py = pybind11;

void register_multisource_py_auto(py::module &_core, Registry &registry) {
{{body}}
}