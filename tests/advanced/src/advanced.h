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