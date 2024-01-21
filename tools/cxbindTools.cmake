function(cxbind_module target_name)
    target_link_libraries(${target_name} PRIVATE cxbind::headers)

    execute_process(
        #COMMAND ${Python_EXECUTABLE} -c "import site; print(site.getsitepackages()[0])"
        COMMAND ${Python_EXECUTABLE} -c "from distutils.sysconfig import get_python_lib; print(get_python_lib())"
        OUTPUT_VARIABLE PYTHON_SITE_PACKAGES
        OUTPUT_STRIP_TRAILING_WHITESPACE
      )
      
    message(STATUS "Python site packages directory: ${PYTHON_SITE_PACKAGES}")
    
    target_include_directories(${target_name} PRIVATE "${PYTHON_SITE_PACKAGES}/cxbind/include")
      
endfunction()