#include <limits>
#include <sstream>

#include <pybind11/pybind11.h>
#include <pybind11/functional.h>
#include <pybind11/stl.h>

#include <cxbind/cxbind.h>
#include "external.h"
#include "internal.h"

namespace py = pybind11;


void register_internal_py(py::module &_tests, Registry &registry) {
}