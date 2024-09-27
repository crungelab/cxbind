# Wrappers

## PyCapsule

Example:

```yaml
'struct.ImGuiContext':
  wrapper: 'PyCapsule'
```

## Custom

Example:

```yaml
'struct.SDL_Window':
  wrapper: 'SDLWindowWrapper'
```

```c++
#include <SDL3/SDL.h>

template<typename T>
class Wrapper {
public:
    Wrapper(T* value) : value(value) {}

    ~Wrapper() {
        // Add custom resource deallocation if needed, like SDL_DestroyWindow for SDL_Window
    }

    T* get() const {
        return value;
    }

    // Add more functionality as needed

private:
    T* value;
};

using SDLWindowWrapper = Wrapper<SDL_Window>;
```

If a struct or class is wrapped during generation we need to check the parameters and return values of all functions/methods we are generating bindings for.

Entries are looked up by the name of the wrapped type.

If an entry exists for a parameter or return node we need to substitute it with the type specified by `wrapper`.