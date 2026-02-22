// namespace test_inits {

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

struct KwInitsUse
{
    int add()
    {
        return a + b;
    }

    int a = 0;
    int b = 0;
    int c = 0;
};

KwInitsUse InitKwInitsUse() {
    KwInitsUse obj;
    obj.a = 1;
    obj.b = 2;
    obj.c = 3;
    return obj;
}

struct ArgsInits
{
    int add()
    {
        return a + b;
    }

    int a = 0;
    int b = 0;
};


//} // namespace test_inits