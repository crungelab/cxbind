#include <limits>

#include <pybind11/pybind11.h>
#include <pybind11/functional.h>
#include <pybind11/stl.h>

#include <cxbind/cxbind.h>
#include "advanced.h"

namespace py = pybind11;

void init_generated(py::module &_core, Registry &registry) {
    PYCLASS_BEGIN(_core, Advanced, Advanced)
        Advanced.def(py::init<>());
        Advanced.def("add", &Advanced::add
        , py::arg("i")
        , py::arg("j")
        , py::return_value_policy::automatic_reference);

    PYCLASS_END(_core, Advanced, Advanced)


}