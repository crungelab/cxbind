cmake_minimum_required(VERSION 3.20...4.0 FATAL_ERROR)

project(cxbind VERSION 0.1.0 LANGUAGES CXX)

include(GNUInstallDirs)
include(CMakePackageConfigHelpers)

#
# Header-only interface library
#
set(cxbind_INCLUDE_DIR
    "${CMAKE_CURRENT_LIST_DIR}/include"
    CACHE INTERNAL "Directory where cxbind headers are located")

add_library(cxbind_headers INTERFACE)
add_library(cxbind::cxbind_headers ALIAS cxbind_headers)  # matches exported target
add_library(cxbind::headers ALIAS cxbind_headers)         # easier to use/remember

target_include_directories(cxbind_headers INTERFACE
    $<BUILD_INTERFACE:${cxbind_INCLUDE_DIR}>
    $<INSTALL_INTERFACE:${CMAKE_INSTALL_INCLUDEDIR}>
)

#
# Install
#
set(CXBIND_CMAKECONFIG_INSTALL_DIR
    "${CMAKE_INSTALL_DATAROOTDIR}/cmake/${PROJECT_NAME}"
    CACHE STRING "install path for cxbindConfig.cmake")

install(DIRECTORY ${cxbind_INCLUDE_DIR}/cxbind
        DESTINATION ${CMAKE_INSTALL_INCLUDEDIR})

write_basic_package_version_file(
    ${CMAKE_CURRENT_BINARY_DIR}/${PROJECT_NAME}ConfigVersion.cmake
    VERSION ${PROJECT_VERSION}
    COMPATIBILITY AnyNewerVersion
    ARCH_INDEPENDENT)

configure_package_config_file(
    tools/${PROJECT_NAME}Config.cmake.in
    ${CMAKE_CURRENT_BINARY_DIR}/${PROJECT_NAME}Config.cmake
    INSTALL_DESTINATION ${CXBIND_CMAKECONFIG_INSTALL_DIR}
    PATH_VARS CMAKE_INSTALL_INCLUDEDIR)

install(
    FILES
        ${CMAKE_CURRENT_BINARY_DIR}/${PROJECT_NAME}Config.cmake
        ${CMAKE_CURRENT_BINARY_DIR}/${PROJECT_NAME}ConfigVersion.cmake
        tools/cxbindTools.cmake
    DESTINATION ${CXBIND_CMAKECONFIG_INSTALL_DIR})

install(TARGETS cxbind_headers EXPORT cxbindTargets)

install(
    EXPORT cxbindTargets
    NAMESPACE "cxbind::"
    DESTINATION ${CXBIND_CMAKECONFIG_INSTALL_DIR})