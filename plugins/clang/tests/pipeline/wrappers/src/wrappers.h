#include "wrappers_detail.h"

//namespace test_wrappers {

void wrapperInFn(SDL_Window* window, int width, int height){}
SDL_Window* wrapperOutFn(){ return nullptr; }
void capsuleInFn(ImGuiContext* context, int width, int height){}
ImGuiContext* capsuleOutFn(int width, int height){ return nullptr; }

struct WrapperStruct
{
    ImGuiContext* context;
    SDL_Window* window;
};

//} // namespace test_wrappers