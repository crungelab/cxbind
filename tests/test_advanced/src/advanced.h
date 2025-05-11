//namespace test_advanced {

int add(int x, int y) {
    return x + y;
}

struct Advanced
{
    Advanced() {}

    int add(int i, int j)
    {
        return i + j;
    }

    // This function should not be exposed
    int ignore_me(int i, int j)
    {
        return i + j;
    }
};

int sub(int x, int y) {
    return x - y;
}

//} // namespace test_advanced