#include <limits>

#include <pybind11/pybind11.h>
#include <pybind11/functional.h>
#include <pybind11/stl.h>

#include <cxbind/cxbind.h>
#include "inits.h"

namespace py = pybind11;

void register_inits_py_auto(py::module &_tests, Registry &registry) {
    py::class_<Inits> _Inits(_tests, "Inits");
    registry.on(_tests, "Inits", _Inits);
        _Inits
        .def(py::init<int>()
        , py::arg("value") = 0
        )
        .def("add", &Inits::add
            , py::arg("i")
            , py::return_value_policy::automatic_reference)
        .def_readwrite("value", &Inits::value)
    ;

    py::class_<KwInits> _KwInits(_tests, "KwInits");
    registry.on(_tests, "KwInits", _KwInits);
        _KwInits
        .def("add", &KwInits::add
            , py::return_value_policy::automatic_reference)
        .def_readwrite("a", &KwInits::a)
        .def_readwrite("b", &KwInits::b)
        .def(py::init([](const py::kwargs& kwargs)
        {
            KwInits obj{};
            if (kwargs.contains("a"))
            {
                auto value = kwargs["a"].cast<int>();
                obj.KwInits::a = value;
            }
            if (kwargs.contains("b"))
            {
                auto value = kwargs["b"].cast<int>();
                obj.KwInits::b = value;
            }
            return obj;
        }), py::return_value_policy::automatic_reference);
    ;


}