function(cxbind_module target_name)
    target_link_libraries(${target_name} PRIVATE cxbind::headers)
endfunction()