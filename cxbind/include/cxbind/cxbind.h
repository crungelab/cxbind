#include <iostream>
#include <map>
#include <functional>
#include <pybind11/pybind11.h>

namespace py = pybind11;

typedef std::function<void(py::detail::generic_type& _class)> RegistryCallback;

class Registry {
    public:
    std::map<std::string, RegistryCallback> callbacks;
    void addCallback(const std::string name, RegistryCallback callback) {
        this->callbacks[name] = callback;
    }
    void on(py::module& _module, const std::string name, py::detail::generic_type& _class) {
        //std::cout << "on register:  " << name << "\n";
        if ( this->callbacks.find(name) == this->callbacks.end() ) { return; }
        this->callbacks[name](_class);
    }
};

#define PYCLASS(_module, _class, _name, ...) py::class_<_class __VA_OPT__(,) __VA_ARGS__> \
    _name(_module, #_name); \
    registry.on(_module, #_name, _name); \
    _name \


#define PYCLASS_BEGIN(_module, _class, _name, ...) py::class_<_class __VA_OPT__(,) __VA_ARGS__> _name(_module, #_name);

#define PYSUBCLASS_BEGIN(_module, _class, _base, _name) py::class_<_class, _base> _name(_module, #_name);

#define PYCLASS_END(_module, _class, _name) registry.on(_module, #_name, _name);

#define PYENUM_SCOPED_BEGIN(_module, _class, _name) py::enum_<_class> _name(_module, #_name, py::arithmetic());
#define PYENUM_SCOPED_END(_module, _class, _name) registry.on(_module, #_name, _name);

#define PYEXTEND_BEGIN(_class, name) \
    registry.addCallback(#name, [](py::detail::generic_type& _type) { \
        py::class_<_class> &_##name = (py::class_<_class>&)_type;

#define PYEXTEND_SCOPED_ENUM_BEGIN(_class, name) \
    registry.addCallback(#name, [](py::detail::generic_type& _type) { \
        py::enum_<_class> &name = (py::enum_<_class>&)_type;

#define PYEXTEND_END });
