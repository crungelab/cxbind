enum DefaultsEnum {
    // Enum values
    DEFAULTS_ENUM_0 = 0,
    DEFAULTS_ENUM_1 = 1,
    DEFAULTS_ENUM_2 = 2,
    DEFAULTS_ENUM_3 = 3,
    DEFAULTS_ENUM_4 = 4,
    DEFAULTS_ENUM_5 = 5,
    DEFAULTS_ENUM_6 = 6,
    DEFAULTS_ENUM_7 = 7,
    DEFAULTS_ENUM_8 = 8,
    DEFAULTS_ENUM_9 = 9
};

enum class DefaultsEnumClass {
    // Enum values
    DEFAULTS_ENUM_CLASS_0 = 0,
    DEFAULTS_ENUM_CLASS_1 = 1,
    DEFAULTS_ENUM_CLASS_2 = 2,
    DEFAULTS_ENUM_CLASS_3 = 3,
    DEFAULTS_ENUM_CLASS_4 = 4,
    DEFAULTS_ENUM_CLASS_5 = 5,
    DEFAULTS_ENUM_CLASS_6 = 6,
    DEFAULTS_ENUM_CLASS_7 = 7,
    DEFAULTS_ENUM_CLASS_8 = 8,
    DEFAULTS_ENUM_CLASS_9 = 9
};

struct Defaults
{
    enum InnerEnum
    {
        // Enum values
        INNER_ENUM_0 = 0,
        INNER_ENUM_1 = 1,
        INNER_ENUM_2 = 2,
        INNER_ENUM_3 = 3,
        INNER_ENUM_4 = 4,
        INNER_ENUM_5 = 5,
        INNER_ENUM_6 = 6,
        INNER_ENUM_7 = 7,
        INNER_ENUM_8 = 8,
        INNER_ENUM_9 = 9
    };
    // Default constructor
    Defaults() {}
    
    int add(int i = 0, int j = DEFAULTS_ENUM_1) const
    {
        return i + j;
    }
    int subtract(int i = 0, int j = InnerEnum::INNER_ENUM_1) const
    {
        return i - j;
    }
    int multiply(int i, int k) const
    {
        return i * k;
    }
};
