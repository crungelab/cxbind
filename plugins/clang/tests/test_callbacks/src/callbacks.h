#include <stdint.h>

typedef bool callback(int value, void* context);

void functionWithCallback(const uint32_t *a, unsigned int count, bool (*callback)(int, void*), void *context)
{
    for (unsigned int i = 0; i < count; ++i)
    {
        callback(a[i], context);
    }
}