#include <stdint.h>

typedef bool callback(int value, void* context);
typedef bool callback2(int value, void* context);

void functionWithCallback(const uint32_t *a, unsigned int count, callback *cb, void *context)
{
    for (unsigned int i = 0; i < count; ++i)
    {
        cb(a[i], context);
    }
}

void functionWithCallback2(const uint32_t *a, unsigned int count, callback2 *cb, void *context)
{
    for (unsigned int i = 0; i < count; ++i)
    {
        cb(a[i], context);
    }
}

void functionWithCallbackSignature(const uint32_t *a, unsigned int count, bool (*cb)(int, void*), void *context)
{
    for (unsigned int i = 0; i < count; ++i)
    {
        cb(a[i], context);
    }
}