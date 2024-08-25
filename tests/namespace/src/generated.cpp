#include <limits>

#include <pybind11/pybind11.h>
#include <pybind11/functional.h>
#include <pybind11/stl.h>

#include <cxbind/cxbind.h>
#include "test.h"

namespace py = pybind11;

void init_generated(py::module &_core, Registry &registry) {
    PYCLASS_BEGIN(_core, other::Other, Other)
        Other.def(py::init<>());
        Other.def("add", &other::Other::add
        , py::arg("i")
        , py::arg("j")
        , py::return_value_policy::automatic_reference);

    PYCLASS_END(_core, other::Other, Other)

    PYCLASS_BEGIN(_core, test::Test, Test)
        Test.def(py::init<>());
        Test.def("add", py::overload_cast<int, int>(&test::Test::add)
        , py::arg("i")
        , py::arg("j")
        , py::return_value_policy::automatic_reference);

        Test.def("add", py::overload_cast<other::Other>(&test::Test::add)
        , py::arg("other")
        , py::return_value_policy::automatic_reference);

    PYCLASS_END(_core, test::Test, Test)


}