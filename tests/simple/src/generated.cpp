#include <limits>

#include <pybind11/pybind11.h>
#include <pybind11/functional.h>
#include <pybind11/stl.h>

#include <cxbind/cxbind.h>
#include "simple.h"

namespace py = pybind11;

void init_generated(py::module &_core, Registry &registry) {
    PYCLASS_BEGIN(_core, Simple, Simple)
        Simple.def(py::init<>());
        Simple.def("add", &Simple::add
        , py::arg("i")
        , py::arg("j")
        , py::return_value_policy::automatic_reference);

    PYCLASS_END(_core, Simple, Simple)


}