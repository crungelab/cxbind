#include "wrappers_detail.h"

//namespace test_wrappers {

void testWrapperIn(SDL_Window* window, int width, int height){}
SDL_Window* testWrapperOut(){ return nullptr; }
void testCapsuleIn(ImGuiContext* context, int width, int height){}
ImGuiContext* testCapsuleOut(int width, int height){ return nullptr; }

//} // namespace test_wrappers