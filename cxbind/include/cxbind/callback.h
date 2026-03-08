#include <pybind11/pybind11.h>
#include <Python.h>        // for PyErr_Fetch / PyErr_Restore

namespace cxbind
{

class thunk_state
{
public:
    thunk_state(py::function callback)
        : cb(std::move(callback))
    {}

    py::function cb;

    // Stored Python exception state (if callback throws)
    bool had_error = false;
    PyObject* err_type = nullptr;
    PyObject* err_value = nullptr;
    PyObject* err_tb = nullptr;
};

} // namespace cxbind