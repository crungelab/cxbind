#include <limits>

#include <pybind11/pybind11.h>
#include <pybind11/functional.h>
#include <pybind11/stl.h>

#include <cxbind/cxbind.h>
#include "enums.h"

namespace py = pybind11;

void register_enums_py_auto(py::module &_tests, Registry &registry) {
    py::enum_<SimpleEnum>(_tests, "SimpleEnum", py::arithmetic())
        .value("VALUE_1", SimpleEnum::VALUE_1)
        .value("VALUE_2", SimpleEnum::VALUE_2)
        .value("VALUE_3", SimpleEnum::VALUE_3)
        .export_values()
    ;
    py::enum_<ScopedEnum>(_tests, "ScopedEnum", py::arithmetic())
        .value("VALUE1", ScopedEnum::Value1)
        .value("VALUE2", ScopedEnum::Value2)
        .value("VALUE3", ScopedEnum::Value3)
    ;
    py::enum_<RedundantEnum>(_tests, "RedundantEnum", py::arithmetic())
        .value("VALUE1", RedundantEnum::RedundantEnumValue1)
        .value("VALUE2", RedundantEnum::RedundantEnumValue2)
        .value("VALUE3", RedundantEnum::RedundantEnumValue3)
        .export_values()
    ;
    py::enum_<ns::NsRedundantEnum>(_tests, "NsRedundantEnum", py::arithmetic())
        .value("VALUE1", ns::NsRedundantEnum::NsRedundantEnumValue1)
        .value("VALUE2", ns::NsRedundantEnum::NsRedundantEnumValue2)
        .value("VALUE3", ns::NsRedundantEnum::NsRedundantEnumValue3)
        .export_values()
    ;
    py::enum_<TypedefEnum>(_tests, "TypedefEnum", py::arithmetic())
        .value("VALUE1", TypedefEnum::TypedefEnumValue1)
        .value("VALUE2", TypedefEnum::TypedefEnumValue2)
        .value("VALUE3", TypedefEnum::TypedefEnumValue3)
        .export_values()
    ;
    py::enum_<EnumStruct::Enum>(_tests, "Enum", py::arithmetic())
        .value("VALUE1", EnumStruct::Enum::Value1)
        .value("VALUE2", EnumStruct::Enum::Value2)
        .value("VALUE3", EnumStruct::Enum::Value3)
        .export_values()
    ;
    py::enum_<primaries::CicpId>(_tests, "PrimariesCicpId", py::arithmetic())
        .value("REC709", primaries::CicpId::Rec709)
        .value("UNSPECIFIED", primaries::CicpId::Unspecified)
        .value("BT2020", primaries::CicpId::Bt2020)
    ;
    py::enum_<transfer::CicpId>(_tests, "TransferCicpId", py::arithmetic())
        .value("REC709", transfer::CicpId::Rec709)
        .value("UNSPECIFIED", transfer::CicpId::Unspecified)
        .value("LINEAR", transfer::CicpId::Linear)
    ;
    py::enum_<left::inner::Level>(_tests, "LeftInnerLevel", py::arithmetic())
        .value("LOW", left::inner::Level::Low)
        .value("HIGH", left::inner::Level::High)
    ;
    py::enum_<right::inner::Level>(_tests, "RightInnerLevel", py::arithmetic())
        .value("LOW", right::inner::Level::Low)
        .value("MID", right::inner::Level::Mid)
        .value("HIGH", right::inner::Level::High)
    ;
    py::class_<Widget> _Widget(_tests, "Widget");
    registry.on(_tests, "Widget", _Widget);
        _Widget
        .def_readwrite("id", &Widget::id)
        ;

        py::enum_<Widget::Kind>(_Widget, "Kind", py::arithmetic())
            .value("SMALL", Widget::Kind::KindSmall)
            .value("LARGE", Widget::Kind::KindLarge)
            .export_values()
        ;
    py::enum_<Gadget::Kind>(_tests, "Kind", py::arithmetic())
        .value("ON", Gadget::Kind::KindOn)
        .value("OFF", Gadget::Kind::KindOff)
        .export_values()
    ;

}