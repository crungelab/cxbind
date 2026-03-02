#include "transforms.h"

TransformsDummy transformsCreateDummy(const Transforms* handle, int value)
{
    return TransformsDummy(value);
}
