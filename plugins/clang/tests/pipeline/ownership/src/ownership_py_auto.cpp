#include <limits>

#include <pybind11/pybind11.h>
#include <pybind11/functional.h>
#include <pybind11/stl.h>

#include <cxbind/cxbind.h>
#include "ownership.h"

namespace py = pybind11;

void register_ownership_py_auto(py::module &_tests, Registry &registry) {
    py::class_<Ownership> _Ownership(_tests, "Ownership");
    registry.on(_tests, "Ownership", _Ownership);
    _tests
    .def("create_ownership", &CreateOwnership
        , py::return_value_policy::reference_internal)
    ;


}