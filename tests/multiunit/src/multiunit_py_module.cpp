#include <pybind11/pybind11.h>

#include <cxbind/cxbind.h>

namespace py = pybind11;

void init_unit_1_py_auto(py::module &, Registry &registry);
void init_unit_2_py_auto(py::module &, Registry &registry);

PYBIND11_MODULE(_core, m)
{
    Registry r;
    init_unit_1_py_auto(m, r);
    init_unit_2_py_auto(m, r);
}