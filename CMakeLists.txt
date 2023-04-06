cmake_minimum_required(VERSION 3.4...3.22 FATAL_ERROR)

project(cxbind VERSION 0.1.0 LANGUAGES CXX)

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

set(CXBIND_HEADERS
    include/cxbind/cxbind.h
)

add_library(cxbind_headers INTERFACE)
add_library(cxbind::cxbind_headers ALIAS cxbind_headers) # to match exported target
add_library(cxbind::headers ALIAS cxbind_headers) # easier to use/remember

target_include_directories(
    cxbind_headers INTERFACE $<BUILD_INTERFACE:${cxbind_INCLUDE_DIR}>
                                                  $<INSTALL_INTERFACE:${CMAKE_INSTALL_INCLUDEDIR}>)


# Cache variable so this can be used in parent projects
set(cxbind_INCLUDE_DIR
    "${CMAKE_CURRENT_LIST_DIR}/include"
    CACHE INTERNAL "Directory where cxbind headers are located")

install(DIRECTORY ${cxbind_INCLUDE_DIR}/cxbind DESTINATION ${CMAKE_INSTALL_INCLUDEDIR})

set(CXBIND_CMAKECONFIG_INSTALL_DIR
"${CMAKE_INSTALL_DATAROOTDIR}/cmake/${PROJECT_NAME}"
CACHE STRING "install path for cxbindConfig.cmake")

write_basic_package_version_file(
    ${CMAKE_CURRENT_BINARY_DIR}/${PROJECT_NAME}ConfigVersion.cmake
    VERSION ${PROJECT_VERSION}
    COMPATIBILITY AnyNewerVersion ARCH_INDEPENDENT)

configure_package_config_file(
    tools/${PROJECT_NAME}Config.cmake.in "${CMAKE_CURRENT_BINARY_DIR}/${PROJECT_NAME}Config.cmake"
    INSTALL_DESTINATION ${CXBIND_CMAKECONFIG_INSTALL_DIR})
    
install(
    FILES ${CMAKE_CURRENT_BINARY_DIR}/${PROJECT_NAME}Config.cmake
            ${CMAKE_CURRENT_BINARY_DIR}/${PROJECT_NAME}ConfigVersion.cmake
            tools/cxbindTools.cmake
    DESTINATION ${CXBIND_CMAKECONFIG_INSTALL_DIR})
    
if(NOT CXBIND_EXPORT_NAME)
    set(CXBIND_EXPORT_NAME "${PROJECT_NAME}Targets")
endif()

install(TARGETS cxbind_headers EXPORT "${CXBIND_EXPORT_NAME}")

install(
EXPORT "${CXBIND_EXPORT_NAME}"
NAMESPACE "cxbind::"
DESTINATION ${CXBIND_CMAKECONFIG_INSTALL_DIR})
    