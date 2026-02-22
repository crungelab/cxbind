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
                obj.a = value;
            }
            if (kwargs.contains("b"))
            {
                auto value = kwargs["b"].cast<int>();
                obj.b = value;
            }
            return obj;
        }));
    ;

    py::class_<KwInitsUse> _KwInitsUse(_tests, "KwInitsUse");
    registry.on(_tests, "KwInitsUse", _KwInitsUse);
        _KwInitsUse
        .def("add", &KwInitsUse::add
            , py::return_value_policy::automatic_reference)
        .def_readwrite("a", &KwInitsUse::a)
        .def_readwrite("b", &KwInitsUse::b)
        .def_readwrite("c", &KwInitsUse::c)
        .def(py::init([](const py::kwargs& kwargs)
        {
            KwInitsUse obj = InitKwInitsUse();
            if (kwargs.contains("a"))
            {
                auto value = kwargs["a"].cast<int>();
                obj.a = value;
            }
            if (kwargs.contains("b"))
            {
                auto value = kwargs["b"].cast<int>();
                obj.b = value;
            }
            if (kwargs.contains("c"))
            {
                auto value = kwargs["c"].cast<int>();
                obj.c = value;
            }
            return obj;
        }));
    ;

    _tests
    .def("init_kw_inits_use", &InitKwInitsUse
        , py::return_value_policy::automatic_reference)
    ;

    py::class_<ArgsInits> _ArgsInits(_tests, "ArgsInits");
    registry.on(_tests, "ArgsInits", _ArgsInits);
        _ArgsInits
        .def("add", &ArgsInits::add
            , py::return_value_policy::automatic_reference)
        .def_readwrite("a", &ArgsInits::a)
        .def_readwrite("b", &ArgsInits::b)
        .def(py::init([](int a, int b)
        {
            ArgsInits obj{};
            obj.a = a;
            obj.b = b;
            return obj;
        }));
    ;


}