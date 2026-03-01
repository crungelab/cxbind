#include <stdint.h>

int facadeFunction(const uint32_t *a, unsigned int count) {
    // Simple function that sums an array of uint32_t
    int sum = 0;
    for (unsigned int i = 0; i < count; ++i) {
        sum += a[i];
    }
    return sum;
}
