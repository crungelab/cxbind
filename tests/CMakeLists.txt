cmake_minimum_required(VERSION 3.4...3.20 FATAL_ERROR)

set(THIS cxbind_tests)
set(MODULE cxbind_tests)

project(${THIS} VERSION 0.1.0 LANGUAGES CXX)

#include(./cmake/Config.cmake)

if (POLICY CMP0054)
    cmake_policy(SET CMP0054 NEW)
endif()

if (POLICY CMP0069)
    cmake_policy(SET CMP0069 NEW)
endif()

if (POLICY CMP0077)
    cmake_policy(SET CMP0077 NEW)
endif()

set_property(GLOBAL PROPERTY USE_FOLDERS ON)

#set (CMAKE_LIBRARY_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR})
#set (CMAKE_RUNTIME_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR})


# Standard includes
include(GNUInstallDirs)
include(CMakePackageConfigHelpers)
include(CMakeDependentOption)

#
# pybind11
#
find_package(Python COMPONENTS Interpreter Development)
#set(-DCMAKE_CXX_STANDARD=20 -std=c++20)
#set(PYBIND11_PYTHON_VERSION 3.10)

#add_subdirectory(depot/pybind11)
add_subdirectory("${CMAKE_SOURCE_DIR}/../depot/pybind11" "${CMAKE_SOURCE_DIR}/build/pybind11")

set(cxbind_DIR "${CMAKE_SOURCE_DIR}/../cxbind/share/cmake/cxbind")
find_package(cxbind REQUIRED)

pybind11_add_module(${THIS} MODULE src/cxbind_tests.cpp)
cxbind_module(${THIS})

#add_custom_command(TARGET ${THIS} 
#                   POST_BUILD
#                   COMMAND ${CMAKE_COMMAND} -E copy $<TARGET_FILE:${THIS}> SomeOtherDir)

add_subdirectory(test_simple)
add_subdirectory(test_advanced)
add_subdirectory(test_arguments)
add_subdirectory(test_enums)
add_subdirectory(test_exclude)
add_subdirectory(test_functions)
add_subdirectory(test_multiunit)
add_subdirectory(test_namespace)
add_subdirectory(test_templates)
