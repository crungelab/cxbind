struct Exclude
{
    Exclude() = default;
    //Exclude() = delete;
    
    int add(int i, int j)
    {
        return i + j;
    }

    int sub(int i, int j)
    {
        return i - j;
    }

    // This function should not be exposed
    int ignore_me(int i, int j)
    {
        return i + j;
    }

    // This function should not be exposed
    int ignore_me_2(int i, int j)
    {
        return i + j;
    }
    
};
