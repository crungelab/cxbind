// namespace test_advanced {

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

//} // namespace test_advanced