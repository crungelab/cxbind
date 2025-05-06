struct OtherClass
{
    int i;
    int j;
};

struct Overloads
{
    Overloads() {}

    int add(int i, int j)
    {
        return i + j;
    }

    double add(const OtherClass& other, double j)
    {
        return other.i + j;
    }

    float add(float i, float j)
    {
        return i + j;
    }

    double add(double i, double j)
    {
        return i + j;
    }
};
