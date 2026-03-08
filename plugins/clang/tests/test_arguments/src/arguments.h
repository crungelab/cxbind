struct Arguments
{
    Arguments() {}

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

void inOutFunction(int i, int* j)
{
    *j = i + *j;
}

int inOutFunctionWithReturn(int i, int* j)
{
    *j = i + *j;
    return *j;
}