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
# One extension module per pipeline case, built into the cxbind_tests package:
#   build/cxbind_tests/test_<case>.so  ->  import cxbind_tests.test_<case>
# Separate modules keep cases from colliding (C++ ODR, pybind11 type registry).
#
set(PACKAGE_DIR "${TESTS_BINARY_DIR}/cxbind_tests")
file(MAKE_DIRECTORY "${PACKAGE_DIR}")
if(NOT EXISTS "${PACKAGE_DIR}/__init__.py")
    file(WRITE "${PACKAGE_DIR}/__init__.py" "")
endif()

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

    # Each generated file defines register_<stem>(); the stem is the name.
    # CONFIGURE_DEPENDS re-runs the glob when units are added or removed.
    file(GLOB GENERATED CONFIGURE_DEPENDS
        "${PIPELINE_DIR}/${case_dir}/src/*_py_auto.cpp")
    if(NOT GENERATED)
        message(STATUS "No generated sources yet for pipeline case: ${case_dir}")
        continue()
    endif()

    set(MODULE "test_${case_dir}")
    set(DECLS "")
    set(CALLS "")
    foreach(src IN LISTS GENERATED)
        get_filename_component(stem "${src}" NAME_WE)
        string(APPEND DECLS "void register_${stem}(py::module &, Registry &registry);\n")
        string(APPEND CALLS "    register_${stem}(m, registry);\n")
    endforeach()

    configure_file(
        "${TESTS_SOURCE_DIR}/src/module_init.cpp.in"
        "${TESTS_BINARY_DIR}/init/${MODULE}.cpp"
        @ONLY
    )

    message(STATUS "Adding pipeline case: ${case_dir} -> cxbind_tests.${MODULE}")

    pybind11_add_module(${MODULE} MODULE
        "${TESTS_BINARY_DIR}/init/${MODULE}.cpp"
        ${GENERATED}
    )
    # Each test module gets its own pybind11 internals, and so its own type
    # registry: cases can bind same-named global types (Widget, Handle)
    # without colliding. Tests only; real modules share internals on purpose.
    target_compile_definitions(${MODULE} PRIVATE
        "PYBIND11_BUILD_ABI=\"_${MODULE}\""
    )

    cxbind_module(${MODULE})


    target_include_directories(${MODULE} PRIVATE "${PIPELINE_DIR}/${case_dir}/src")
    set_target_properties(${MODULE} PROPERTIES
        LIBRARY_OUTPUT_DIRECTORY "${PACKAGE_DIR}"
    )

endforeach()