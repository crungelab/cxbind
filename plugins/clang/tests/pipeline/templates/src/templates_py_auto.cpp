#include <limits>

#include <pybind11/pybind11.h>
#include <pybind11/functional.h>
#include <pybind11/stl.h>

#include <cxbind/cxbind.h>
#include "templates.h"

namespace py = pybind11;

void register_templates_py_auto(py::module &_tests, Registry &registry) {
    py::class_<MyClass<float, double>> _MyClassFloatDouble(_tests, "MyClassFloatDouble");
    registry.on(_tests, "MyClassFloatDouble", _MyClassFloatDouble);
        _MyClassFloatDouble
        .def(py::init<float, double>()
        , py::arg("value")
        , py::arg("value2")
        )
        .def("set_value", &MyClass<float, double>::setValue
            , py::arg("value")
            )
        .def("get_value", &MyClass<float, double>::getValue
            )
        .def("do_this", &MyClass<float, double>::doThis
            , py::arg("values")
            )
        .def("do_that", [](MyClass<float, double>& self, std::array<float, 3>& bmin)
            {
                return self.doThat(&bmin[0]);
            }
            , py::arg("bmin")
            )
    ;

    py::class_<MyClass2<int>> _MyClassI(_tests, "MyClassI");
    registry.on(_tests, "MyClassI", _MyClassI);
        _MyClassI
        .def(py::init<>())
        .def(py::init<int>()
        , py::arg("value")
        )
        .def("set_value", &MyClass2<int>::setValue
            , py::arg("value")
            )
        .def("get_value", &MyClass2<int>::getValue
            )
    ;

    _tests
    .def("my_function_float", &myFunction<float>
        )
    .def("my_function_i", &myFunction<int>
        )
    ;


}