// namespace test_inits {

struct Handle
{
    Handle(int value = 0) : value(value) {}

    int value = 0;
};

struct Dummy
{
    Dummy(int value = 0) : value(value) {}

    int value = 0;
};

Dummy handleCreateDummy(const Handle* handle, int value)
{
    return Dummy(value);
}


//} // namespace test_inits