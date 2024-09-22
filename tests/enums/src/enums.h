enum SimpleEnum {
  ENUM_VALUE_1,
  ENUM_VALUE_2,
  ENUM_VALUE_3
};

enum class ScopedEnum {
  Value1,
  Value2,
  Value3
};

// Strip enum name from enum constant names
enum RedundantEnum {
  RedundantEnumValue1,
  RedundantEnumValue2,
  RedundantEnumValue3
};

// Strip enum name from enum constant names
namespace ns {
enum RedundantEnum {
  RedundantEnumValue1,
  RedundantEnumValue2,
  RedundantEnumValue3
};
};
