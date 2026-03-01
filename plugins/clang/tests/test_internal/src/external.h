#pragma once

struct Handle
{
    Handle(int value = 0) : value(value) {}

    int value = 0;
};

struct Dummy
{
    Dummy(int value = 0) : value(value) {}

    int value = 0;
};

/*
Dummy handleCreateDummy(const Handle* handle, int value)
{
    return Dummy(value);
}
*/