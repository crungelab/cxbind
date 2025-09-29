//namespace test_advanced {

int add(int x, int y) {
    return x + y;
}

struct Advanced
{
    Advanced(int value = 0) : value(value) {}

    int add(int i)
    {
        return i + value;
    }

    // This function should not be exposed
    int ignore_me(int i)
    {
        return i + value;
    }

    int value = 0;
};

int sub(int x, int y) {
    return x - y;
}

//} // namespace test_advanced