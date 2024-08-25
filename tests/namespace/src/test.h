namespace other {

struct Other
{
    Other() {}
    
    int add(int i, int j)
    {
        return i + j;
    }
};

}

namespace test {

struct Test
{
    Test() {}
    
    int add(int i, int j)
    {
        return i + j;
    }
    int add(other::Other other)
    {
        return other.add(1, 2);
    }
};

} // namespace test