int facadeFunction(unsigned int count, const uint32_t *a) {
    // Simple function that sums an array of uint32_t
    int sum = 0;
    for (unsigned int i = 0; i < count; ++i) {
        sum += a[i];
    }
    return sum;
}

int facadeFunction2(unsigned int count, uint32_t *a) {
    // Simple function that sums an array of uint32_t
    int sum = 0;
    for (unsigned int i = 0; i < count; ++i) {
        sum += a[i];
    }
    return sum;
}