#pragma once

// Ownership test cases. Each struct counts its live instances so the Python
// tests can observe whether an object was really deleted (or not) when its
// wrapper was garbage-collected, instead of trusting the generated policy.
//
// Functions here must not be `inline`: cxbind skips inline functions.

static int g_live_widgets = 0;
static int g_live_handles = 0;
static int g_live_parents = 0;

int LiveWidgets() { return g_live_widgets; }
int LiveHandles() { return g_live_handles; }
int LiveParents() { return g_live_parents; }

// ---------------------------------------------------------------------------
// Inferred ownership (no spec)
// ---------------------------------------------------------------------------

struct Widget
{
    int value = 0;
    Widget() { ++g_live_widgets; }
    Widget(const Widget& other) : value(other.value) { ++g_live_widgets; }
    ~Widget() { --g_live_widgets; }
};

// T& -> REF: Python must reference the C++ object, so writes reach it.
Widget& GetWidgetRef()
{
    static Widget widget;
    return widget;
}

int GetWidgetRefValue() { return GetWidgetRef().value; }

// T* -> REF: the library owns it; Python must never delete it.
Widget* GetWidgetPtr()
{
    static Widget widget;
    return &widget;
}

// T -> automatic: Python gets (and owns) its own copy.
Widget MakeWidget()
{
    Widget widget;
    widget.value = 7;
    return widget;
}

// ---------------------------------------------------------------------------
// Explicit ownership on the function
// ---------------------------------------------------------------------------

// spec: returns ownership owned -> take_ownership; Python deletes it.
Widget* CreateWidget() { return new Widget(); }

// ---------------------------------------------------------------------------
// Regression: the returned type has a spec that doesn't set ownership.
// A spec existing (here only for stub lines) must not switch off inference.
// ---------------------------------------------------------------------------

struct Settings
{
    int level = 0;
};

Settings& GetSettings()
{
    static Settings settings;
    return settings;
}

Settings* GetSettingsPtr() { return &GetSettings(); }

int GetSettingsLevel() { return GetSettings().level; }

// ---------------------------------------------------------------------------
// Explicit ownership on the type, and a function spec overriding it
// ---------------------------------------------------------------------------

struct Handle
{
    int id = 0;
    Handle() { ++g_live_handles; }
    ~Handle() { --g_live_handles; }
};

// Type spec: ownership owned -> Python deletes it.
Handle* NewHandle() { return new Handle(); }

// Function spec: ownership ref, beats the type's `owned`.
Handle* PeekHandle()
{
    static Handle handle;
    return &handle;
}

// ---------------------------------------------------------------------------
// Borrowed: an internal pointer keeps its owner alive (reference_internal)
// ---------------------------------------------------------------------------

struct Child
{
    int value = 5;
};

struct Parent
{
    Child child;
    Parent() { ++g_live_parents; }
    ~Parent() { --g_live_parents; }

    // spec: returns ownership borrowed
    Child* GetChild() { return &child; }
};