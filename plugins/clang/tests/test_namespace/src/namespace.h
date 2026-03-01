namespace ns1 {

struct Ns1
{
    Ns1() {}
    
    int add(int i, int j)
    {
        return i + j;
    }
};

} // namespace ns1

namespace ns2 {

struct Ns2
{
    Ns2() {}
    
    int add(int i, int j)
    {
        return i + j;
    }
    int add(ns1::Ns1 other)
    {
        return other.add(1, 2);
    }
};

} // namespace ns2