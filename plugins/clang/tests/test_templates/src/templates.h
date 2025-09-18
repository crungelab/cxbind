template <typename T, typename U>
class MyClass {
public:
    MyClass(T value, U value2) : value_(value), value_2_(value2) {}
    void setValue(T value) { value_ = value; }
    T getValue() const { return value_; }
    T doThis(const std::array<T, 3> &values) {
        T sum = 0;
        for (const auto &value : values) {
            sum += value;
        }
        return sum;
    }
    void doThat(T bmin[3]) {
        for (int i = 0; i < 3; ++i) {
            bmin[i] = value_;
        }
    }

private:
    T value_;
    U value_2_;
};

template <typename T>
class MyClass2 {
public:
    MyClass2(T value) : value_(value) {}
    void setValue(T value) { value_ = value; }
    T getValue() const { return value_; }

private:
    T value_;
};