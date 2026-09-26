#include <limits>

#include <pybind11/pybind11.h>
#include <pybind11/functional.h>
#include <pybind11/stl.h>

#include <cxbind/cxbind.h>

#include "ownership.h"

namespace py = pybind11;

void register_ownership_py_auto(py::module &_tests, Registry &registry) {
    _tests
    .def("live_widgets", &LiveWidgets
        )
    .def("live_handles", &LiveHandles
        )
    .def("live_parents", &LiveParents
        )
    ;

    py::class_<Widget> _Widget(_tests, "Widget");
    registry.on(_tests, "Widget", _Widget);
        _Widget
        .def_readwrite("value", &Widget::value)
        .def(py::init<>())
    ;

    _tests
    .def("get_widget_ref", &GetWidgetRef
        , py::return_value_policy::reference)
    .def("get_widget_ref_value", &GetWidgetRefValue
        )
    .def("get_widget_ptr", &GetWidgetPtr
        , py::return_value_policy::reference)
    .def("make_widget", &MakeWidget
        )
    .def("create_widget", &CreateWidget
        , py::return_value_policy::take_ownership)
    ;

    py::class_<Settings> _Settings(_tests, "Settings");
    registry.on(_tests, "Settings", _Settings);
        _Settings
        .def_readwrite("level", &Settings::level)
    ;

    _tests
    .def("get_settings", &GetSettings
        , py::return_value_policy::reference)
    .def("get_settings_ptr", &GetSettingsPtr
        , py::return_value_policy::reference)
    .def("get_settings_level", &GetSettingsLevel
        )
    ;

    py::class_<Handle> _Handle(_tests, "Handle");
    registry.on(_tests, "Handle", _Handle);
        _Handle
        .def_readwrite("id", &Handle::id)
        .def(py::init<>())
    ;

    _tests
    .def("new_handle", &NewHandle
        , py::return_value_policy::take_ownership)
    .def("peek_handle", &PeekHandle
        , py::return_value_policy::reference)
    ;

    py::class_<Child> _Child(_tests, "Child");
    registry.on(_tests, "Child", _Child);
        _Child
        .def_readwrite("value", &Child::value)
    ;

    py::class_<Parent> _Parent(_tests, "Parent");
    registry.on(_tests, "Parent", _Parent);
        _Parent
        .def_readwrite("child", &Parent::child)
        .def(py::init<>())
        .def("get_child", &Parent::GetChild
            , py::return_value_policy::reference_internal)
    ;


}
