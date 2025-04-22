#include <limits>

#include <pybind11/pybind11.h>
#include <pybind11/functional.h>
#include <pybind11/stl.h>

#include <cxbind/cxbind.h>
#include "templates.h"

namespace py = pybind11;

void register_templates_py_auto(py::module &_core, Registry &registry) {
    py::class_<MyClass<float, double>> MyClass_float_double(_core, "MyClass_float_double");
    registry.on(_core, "MyClass_float_double", MyClass_float_double);
    MyClass_float_double
        .def(py::init<float, double>()
        , py::arg("value")
        , py::arg("value2")
        )
        .def("set_value", &MyClass<float, double>::setValue
            , py::arg("value")
            , py::return_value_policy::automatic_reference)
        .def("get_value", &MyClass<float, double>::getValue
            , py::return_value_policy::automatic_reference)
        .def("do_this", &MyClass<float, double>::doThis
            , py::arg("values")
            , py::return_value_policy::automatic_reference)
        .def("do_that", [](MyClass<float, double>& self, std::array<float, 3>& bmin)
            {
                self.doThat(&bmin[0]);
                return bmin;
            }
            , py::arg("bmin")
            , py::return_value_policy::automatic_reference)
    ;

    py::class_<MyClass2<int>> MyClass2_int(_core, "MyClass2_int");
    registry.on(_core, "MyClass2_int", MyClass2_int);
    MyClass2_int
        .def(py::init<int>()
        , py::arg("value")
        )
        .def("set_value", &MyClass2<int>::setValue
            , py::arg("value")
            , py::return_value_policy::automatic_reference)
        .def("get_value", &MyClass2<int>::getValue
            , py::return_value_policy::automatic_reference)
    ;


}