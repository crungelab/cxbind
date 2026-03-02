//namespace test_wrappers {
template<typename T>
class Wrapper {
public:
    Wrapper(T* value) : value(value) {}

    ~Wrapper() {
        // Add custom resource deallocation if needed, like SDL_DestroyWindow for SDL_Window
    }

    // Implicit conversion operator to T*
    operator T*() const {
        return value;
    }

    T* get() const {
        return value;
    }

    // Add more functionality as needed

private:
    T* value;
};

typedef struct SDL_Window SDL_Window;

using SDLWindowWrapper = Wrapper<SDL_Window>;

//} // namespace test_wrappers