cmake_minimum_required(VERSION 3.4...3.20 FATAL_ERROR)

set(THIS cxbind_tests)
set(MODULE cxbind_tests)

project(${THIS} VERSION 0.1.0 LANGUAGES CXX)

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


# Standard includes
include(GNUInstallDirs)
include(CMakePackageConfigHelpers)
include(CMakeDependentOption)

#
# pybind11
#
find_package(Python COMPONENTS Interpreter Development)

add_subdirectory("${CMAKE_SOURCE_DIR}/../../../depot/pybind11" "${CMAKE_SOURCE_DIR}/build/pybind11")

set(cxbind_DIR "${CMAKE_SOURCE_DIR}/../../../cxbind/share/cmake/cxbind")
find_package(cxbind REQUIRED)

pybind11_add_module(${THIS} MODULE src/cxbind_tests.cpp)
cxbind_module(${THIS})

add_subdirectory(test_simple)
add_subdirectory(test_advanced)
add_subdirectory(test_arguments)
add_subdirectory(test_enums)
add_subdirectory(test_exclude)
add_subdirectory(test_functions)
add_subdirectory(test_inits)
add_subdirectory(test_multiunit)
add_subdirectory(test_namespace)
add_subdirectory(test_overloads)
add_subdirectory(test_defaults)
add_subdirectory(test_multisource)
add_subdirectory(test_templates)
add_subdirectory(test_aliases)
add_subdirectory(test_properties)
add_subdirectory(test_bitfields)
