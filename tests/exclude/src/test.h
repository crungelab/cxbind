struct Test
{
    Test() = delete;
    
    int add(int i, int j)
    {
        return i + j;
    }
};
