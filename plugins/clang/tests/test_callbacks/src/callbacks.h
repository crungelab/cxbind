#include <stdint.h>

bool callback(int value) {
    return value % 2 == 0;
}

void functionWithCallback(const uint32_t *a, unsigned int count, bool (*callback)(int)) {
    for (unsigned int i = 0; i < count; ++i) {
        callback(a[i]);
    }
}