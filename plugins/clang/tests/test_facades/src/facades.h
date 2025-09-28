int facadeFunction(unsigned int count, uint_32 *a) {
    // Simple function that sums an array of uint_32
    int sum = 0;
    for (unsigned int i = 0; i < count; ++i) {
        sum += a[i];
    }
    return sum;
}