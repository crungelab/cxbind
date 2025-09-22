#include <limits>

#include <pybind11/pybind11.h>
#include <pybind11/functional.h>
#include <pybind11/stl.h>

#include <cxbind/cxbind.h>
#include "aliases.h"

namespace py = pybind11;

using AliasClassI = AliasClass<int>;

using IntAddPtr = int (*)(int, int); 
IntAddPtr aliasFunctionI = &aliasFunction<int>;

void register_aliases_py_auto(py::module &_tests, Registry &registry) {
{{body}}
}