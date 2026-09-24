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
            )
        .def_readwrite("value", &Inits::value)
    ;

    py::class_<KwInits> _KwInits(_tests, "KwInits");
    registry.on(_tests, "KwInits", _KwInits);
        _KwInits
        .def("add", &KwInits::add
            )
        .def_readwrite("a", &KwInits::a)
        .def_readwrite("b", &KwInits::b)
        .def(py::init([](const py::kwargs& kwargs)
        {
            KwInits obj{};
            static const std::unordered_set<std::string> allowed_keys = {"a", "b"};
            for (auto item : kwargs)
            {
                std::string key = py::str(item.first);
                if (allowed_keys.find(key) == allowed_keys.end())
                {
                    throw py::value_error("Unexpected keyword argument: '" + key + "'");
                }
            }
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
        }))
    ;

    py::class_<KwInitsUse> _KwInitsUse(_tests, "KwInitsUse");
    registry.on(_tests, "KwInitsUse", _KwInitsUse);
        _KwInitsUse
        .def("add", &KwInitsUse::add
            )
        .def_readwrite("a", &KwInitsUse::a)
        .def_readwrite("b", &KwInitsUse::b)
        .def_readwrite("c", &KwInitsUse::c)
        .def(py::init([](const py::kwargs& kwargs)
        {
            KwInitsUse obj = InitKwInitsUse();
            static const std::unordered_set<std::string> allowed_keys = {"a", "b", "c"};
            for (auto item : kwargs)
            {
                std::string key = py::str(item.first);
                if (allowed_keys.find(key) == allowed_keys.end())
                {
                    throw py::value_error("Unexpected keyword argument: '" + key + "'");
                }
            }
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
        }))
    ;

    _tests
    .def("init_kw_inits_use", &InitKwInitsUse
        )
    ;

    py::class_<KwInitsBase> _KwInitsBase(_tests, "KwInitsBase");
    registry.on(_tests, "KwInitsBase", _KwInitsBase);
        _KwInitsBase
        .def("add", &KwInitsBase::add
            )
        .def_readwrite("a", &KwInitsBase::a)
        .def_readwrite("b", &KwInitsBase::b)
    ;

    py::class_<KwInitsFlatten> _KwInitsFlatten(_tests, "KwInitsFlatten");
    registry.on(_tests, "KwInitsFlatten", _KwInitsFlatten);
        _KwInitsFlatten
        .def("add", &KwInitsFlatten::add
            )
        .def_property("a",
            [](const KwInitsFlatten& self){ return self.base.a; },
            [](KwInitsFlatten& self, int value){ self.base.a = value; }
        )
        .def_property("b",
            [](const KwInitsFlatten& self){ return self.base.b; },
            [](KwInitsFlatten& self, int value){ self.base.b = value; }
        )
        .def(py::init([](const py::kwargs& kwargs)
        {
            KwInitsFlatten obj = InitKwInitsFlatten();
            static const std::unordered_set<std::string> allowed_keys = {"a", "b"};
            for (auto item : kwargs)
            {
                std::string key = py::str(item.first);
                if (allowed_keys.find(key) == allowed_keys.end())
                {
                    throw py::value_error("Unexpected keyword argument: '" + key + "'");
                }
            }
            if (kwargs.contains("a"))
            {
                auto value = kwargs["a"].cast<int>();
                obj.base.a = value;
            }
            if (kwargs.contains("b"))
            {
                auto value = kwargs["b"].cast<int>();
                obj.base.b = value;
            }
            return obj;
        }))
    ;

    _tests
    .def("init_kw_inits_flatten", &InitKwInitsFlatten
        )
    ;

    py::class_<ArgsInits> _ArgsInits(_tests, "ArgsInits");
    registry.on(_tests, "ArgsInits", _ArgsInits);
        _ArgsInits
        .def("add", &ArgsInits::add
            )
        .def_readwrite("a", &ArgsInits::a)
        .def_readwrite("b", &ArgsInits::b)
        .def(py::init([](int a, int b)
        {
            ArgsInits obj{};
            obj.a = a;
            obj.b = b;
            return obj;
        }))
    ;


}