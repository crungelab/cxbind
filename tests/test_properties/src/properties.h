struct Properties
{
    Properties() : x(0) {}

    int getX() const { return x; }
    void setX(int value) { x = value; }

    int getY() const { return x + 1; }

    int add(int i, int j)
    {
        return i + j;
    }

    int x = 0;
};
