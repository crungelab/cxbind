#include <pybind11/pybind11.h>

#include <cxbind/cxbind.h>

namespace py = pybind11;

void init_main(py::module &, Registry &registry);
void init_generated(py::module &, Registry &registry);

PYBIND11_MODULE(_core, m)
{
    Registry r;
    init_generated(m, r);
}