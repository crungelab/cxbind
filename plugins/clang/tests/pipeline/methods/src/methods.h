#pragma once

struct Methods
{
    Methods(int value = 0) : value(value) {}

    int add(int i)
    {
        return i + value;
    }

    // This function should not be exposed
    int ignore_me(int i)
    {
        return i + value;
    }

    // -----------------------------------------------------------------------
    // Static/instance collision, instance declared first.
    // Both format to "equals": the instance keeps it, the static becomes
    // "equals_static". Different C++ spellings, so no overload_cast needed.
    // -----------------------------------------------------------------------

    bool equals(const Methods& other) const
    {
        return value == other.value;
    }

    static bool Equals(const Methods& a, const Methods& b)
    {
        return a.value == b.value;
    }

    // -----------------------------------------------------------------------
    // Same collision, static declared first.
    // The static is still the one renamed: resolution doesn't depend on order.
    // -----------------------------------------------------------------------

    static int Compare(const Methods& a, const Methods& b)
    {
        return (a.value > b.value) - (a.value < b.value);
    }

    int compare(const Methods& other) const
    {
        return Compare(*this, other);
    }

    // -----------------------------------------------------------------------
    // Collision where the static side is a C++ overload set.
    // All Scale overloads move to "scale_static" together and stay one Python
    // overload set; overload_cast is still keyed on the C++ spelling, so it's
    // emitted for Scale but not for scale.
    // -----------------------------------------------------------------------

    int scale(int factor) const
    {
        return value * factor;
    }

    static int Scale(const Methods& m, int factor)
    {
        return m.value * factor;
    }

    static int Scale(const Methods& m, int factor, int offset)
    {
        return m.value * factor + offset;
    }

    // -----------------------------------------------------------------------
    // Static with no instance counterpart keeps its plain name.
    // -----------------------------------------------------------------------

    static Methods Make(int value)
    {
        return Methods(value);
    }

    int value = 0;
};