//namespace test_inits {

struct Inits
{
    Inits(int value = 0) : value(value) {}

    int add(int i)
    {
        return i + value;
    }

    int value = 0;
};

struct KwInits
{
    int add()
    {
        return a + b;
    }

    int a = 0;
    int b = 0;
};

//} // namespace test_inits