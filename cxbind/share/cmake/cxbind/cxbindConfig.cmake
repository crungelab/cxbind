
####### Expanded from @PACKAGE_INIT@ by configure_package_config_file() #######
####### Any changes to this file will be overwritten by the next CMake run ####
####### The input file was cxbindConfig.cmake.in                            ########

get_filename_component(PACKAGE_PREFIX_DIR "${CMAKE_CURRENT_LIST_DIR}/../../../" ABSOLUTE)

macro(set_and_check _var _file)
  set(${_var} "${_file}")
  if(NOT EXISTS "${_file}")
    message(FATAL_ERROR "File or directory ${_file} referenced by variable ${_var} does not exist !")
  endif()
endmacro()

macro(check_required_components _NAME)
  foreach(comp ${${_NAME}_FIND_COMPONENTS})
    if(NOT ${_NAME}_${comp}_FOUND)
      if(${_NAME}_FIND_REQUIRED_${comp})
        set(${_NAME}_FOUND FALSE)
      endif()
    endif()
  endforeach()
endmacro()

####################################################################################

# Location of cxbind/cxbind.h
# This will be relative unless explicitly set as absolute
set(cxbind_INCLUDE_DIR "")

set(cxbind_LIBRARY "")
set(cxbind_DEFINITIONS USING_cxbind)
set(cxbind_VERSION_TYPE "")

check_required_components(cxbind)

include("${CMAKE_CURRENT_LIST_DIR}/cxbindTargets.cmake")

# Easier to use / remember
add_library(cxbind::headers IMPORTED INTERFACE)
set_target_properties(cxbind::headers PROPERTIES INTERFACE_LINK_LIBRARIES
                                                   cxbind::cxbind_headers)

include("${CMAKE_CURRENT_LIST_DIR}/cxbindTools.cmake")

if(NOT cxbind_FIND_QUIETLY)
  message(
    STATUS
      "Found cxbind: ${cxbind_INCLUDE_DIR} (found version \"${cxbind_VERSION}${cxbind_VERSION_TYPE}\")"
  )
endif()
