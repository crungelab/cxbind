enum SimpleEnum {
  VALUE_1,
  VALUE_2,
  VALUE_3
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
enum NsRedundantEnum {
  NsRedundantEnumValue1,
  NsRedundantEnumValue2,
  NsRedundantEnumValue3
};
};
