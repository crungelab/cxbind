#include <limits>

#include <pybind11/pybind11.h>
#include <pybind11/functional.h>
#include <pybind11/stl.h>

#include <cxbind/cxbind.h>
#include "bitfields.h"

namespace py = pybind11;

void register_bitfields_py_auto(py::module &_tests, Registry &registry) {
    py::class_<Bitfields> _Bitfields(_tests, "Bitfields");
    registry.on(_tests, "Bitfields", _Bitfields);
        _Bitfields
        .def(py::init<>())
        .def_property("x",
            [](Bitfields& self){ return self.x; },
            [](Bitfields& self, int source){ self.x = source; }
        )
        .def_property("y",
            [](Bitfields& self){ return self.y; },
            [](Bitfields& self, int source){ self.y = source; }
        )
        .def_property("z",
            [](Bitfields& self){ return self.z; },
            [](Bitfields& self, int source){ self.z = source; }
        )
    ;


}