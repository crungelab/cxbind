// namespace test_inits {

struct Repr
{
    Repr(int value = 0) : value(value) {}

    int add(int i)
    {
        return i + value;
    }

    int value = 0;
};



//} // namespace test_inits