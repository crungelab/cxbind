#pragma once

// ---------------------------------------------------------------------------
// Basic cases
// ---------------------------------------------------------------------------

enum SimpleEnum
{
    VALUE_1,
    VALUE_2,
    VALUE_3
};

// Scoped enum: constants stay scoped (no export_values)
enum class ScopedEnum
{
    Value1,
    Value2,
    Value3
};

// Strip enum name from enum constant names
enum RedundantEnum
{
    RedundantEnumValue1,
    RedundantEnumValue2,
    RedundantEnumValue3
};

// Strip enum name from enum constant names; namespace is flattened
namespace ns
{
    enum NsRedundantEnum
    {
        NsRedundantEnumValue1,
        NsRedundantEnumValue2,
        NsRedundantEnumValue3
    };
};

// Typedef enum
typedef enum
{
    TypedefEnumValue1,
    TypedefEnumValue2,
    TypedefEnumValue3
} TypedefEnum;

// Pre c++11 scoped enum
struct EnumStruct
{
    enum Enum
    {
        Value1,
        Value2,
        Value3
    };
};

// ---------------------------------------------------------------------------
// Collision: same enum name in two flattened namespaces
// (mirrors SkNamedPrimaries::CicpId / SkNamedTransferFn::CicpId)
// Expected: PrimariesCicpId, TransferCicpId; no bare CicpId.
// ---------------------------------------------------------------------------

namespace primaries
{
    enum class CicpId
    {
        Rec709 = 1,
        Unspecified = 2,
        Bt2020 = 9
    };
};

namespace transfer
{
    enum class CicpId
    {
        Rec709 = 1,
        Unspecified = 2,
        Linear = 8
    };
};

// ---------------------------------------------------------------------------
// Collision that one level of qualification can't resolve
// Level -> InnerLevel (still colliding) -> LeftInnerLevel / RightInnerLevel
// ---------------------------------------------------------------------------

namespace left
{
    namespace inner
    {
        enum class Level
        {
            Low,
            High
        };
    };
};

namespace right
{
    namespace inner
    {
        enum class Level
        {
            Low,
            Mid,
            High
        };
    };
};

// Same enum name in a bound struct and an enum-only struct.
// Widget has a field, so it's bound and Kind nests inside it.
// Gadget has only the enum, so its Kind flattens to module scope.
// Different scopes: no collision, no renames.

struct Widget
{
    int id;
    enum Kind
    {
        KindSmall,
        KindLarge
    };
};

struct Gadget
{
    enum Kind
    {
        KindOn,
        KindOff
    };
};