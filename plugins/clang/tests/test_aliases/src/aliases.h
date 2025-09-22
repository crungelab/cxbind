template <typename T>
class AliasClass {
public:
    AliasClass(T value) : value_(value) {}
    void setValue(T value) { value_ = value; }
    T getValue() const { return value_; }

private:
    T value_;
};

template <typename T>
T aliasFunction(T a, T b) {
    return a + b;
}