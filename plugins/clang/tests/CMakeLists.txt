cmake_minimum_required(VERSION 3.16...3.28 FATAL_ERROR)

project(cxbind_tests VERSION 0.1.0 LANGUAGES CXX)

set(THIS cxbind_tests)
set(MODULE cxbind_tests)

if(POLICY CMP0054)
    cmake_policy(SET CMP0054 NEW)
endif()

if(POLICY CMP0069)
    cmake_policy(SET CMP0069 NEW)
endif()

if(POLICY CMP0077)
    cmake_policy(SET CMP0077 NEW)
endif()

set_property(GLOBAL PROPERTY USE_FOLDERS ON)

include(GNUInstallDirs)
include(CMakePackageConfigHelpers)
include(CMakeDependentOption)

#
# Paths
#
set(TESTS_SOURCE_DIR "${CMAKE_CURRENT_SOURCE_DIR}")
set(TESTS_BINARY_DIR "${CMAKE_CURRENT_BINARY_DIR}")
set(PIPELINE_DIR "${TESTS_SOURCE_DIR}/pipeline")

#
# Python / pybind11
#
find_package(Python REQUIRED COMPONENTS Interpreter Development)

add_subdirectory(
    "${TESTS_SOURCE_DIR}/../../../depot/pybind11"
    "${TESTS_BINARY_DIR}/pybind11"
)

#
# cxbind
#
set(cxbind_DIR "${TESTS_SOURCE_DIR}/../../../cxbind/share/cmake/cxbind")
find_package(cxbind REQUIRED)

#
# Root module
#
pybind11_add_module(${THIS} MODULE src/cxbind_tests.cpp)
cxbind_module(${THIS})

#
# Pipeline exclusion list
#
set(PIPELINE_SKIP
    # examples
    #callbacks
    #templates
)

#
# Discover pipeline test cases
#
file(GLOB PIPELINE_CASE_DIRS RELATIVE "${PIPELINE_DIR}" "${PIPELINE_DIR}/*")

foreach(case_dir IN LISTS PIPELINE_CASE_DIRS)

    if(NOT IS_DIRECTORY "${PIPELINE_DIR}/${case_dir}")
        continue()
    endif()

    # skip excluded directories
    list(FIND PIPELINE_SKIP "${case_dir}" SKIP_INDEX)
    if(NOT SKIP_INDEX EQUAL -1)
        message(STATUS "Skipping pipeline case: ${case_dir}")
        continue()
    endif()

    if(EXISTS "${PIPELINE_DIR}/${case_dir}/CMakeLists.txt")
        message(STATUS "Adding pipeline case: ${case_dir}")

        add_subdirectory(
            "${PIPELINE_DIR}/${case_dir}"
            "${TESTS_BINARY_DIR}/pipeline/${case_dir}"
        )

    endif()

endforeach()