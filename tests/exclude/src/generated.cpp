#include <limits>

#include <pybind11/pybind11.h>
#include <pybind11/functional.h>
#include <pybind11/stl.h>

#include <cxbind/cxbind.h>
#include "test.h"

namespace py = pybind11;

void init_generated(py::module &_core, Registry &registry) {
    PYCLASS_BEGIN(_core, Test, Test)
        Test.def("add", &Test::add
        , py::arg("i")
        , py::arg("j")
        , py::return_value_policy::automatic_reference);

    PYCLASS_END(_core, Test, Test)


}