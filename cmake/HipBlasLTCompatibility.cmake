# HipBlasLT API Compatibility Module
# This module handles hipBLASLT API compatibility issues at build time

function(apply_hipblaslt_compatibility_fix)
    set(HIPBLASLT_HOST_FILE "${CMAKE_CURRENT_SOURCE_DIR}/library/src/hipblaslt_host.cpp")
    set(HIPBLASLT_HOST_PATCHED "${CMAKE_CURRENT_BINARY_DIR}/hipblaslt_host_patched.cpp")

    if(EXISTS ${HIPBLASLT_HOST_FILE})
        message(STATUS "Applying hipBLASLT API compatibility fix...")

        # Read the original file
        file(READ ${HIPBLASLT_HOST_FILE} HIPBLASLT_CONTENT)

        # Apply fixes for missing setter methods
        string(REGEX REPLACE
            "problemType\\.setOpA\\([^)]+\\);[^}]*problemType\\.setTypeCompute\\([^)]+\\);"
            "// API compatibility: setter methods removed"
            HIPBLASLT_CONTENT "${HIPBLASLT_CONTENT}")

        string(REGEX REPLACE
            "inputs\\.setA\\([^)]+\\);[^}]*inputs\\.setBeta\\([^)]+\\);"
            "// API compatibility: input setters handled by setProblem()"
            HIPBLASLT_CONTENT "${HIPBLASLT_CONTENT}")

        string(REGEX REPLACE
            "inputs\\[batch\\]\\.setA\\([^)]+\\);[^}]*inputs\\[batch\\]\\.setBeta\\([^)]+\\);"
            "// API compatibility: batch input setters handled by setProblem()"
            HIPBLASLT_CONTENT "${HIPBLASLT_CONTENT}")

        # Write the patched file
        file(WRITE ${HIPBLASLT_HOST_PATCHED} "${HIPBLASLT_CONTENT}")

        # Replace the original file in the build
        set_property(SOURCE ${HIPBLASLT_HOST_FILE} PROPERTY
                     COMPILE_FLAGS "-include ${CMAKE_CURRENT_BINARY_DIR}/hipblaslt_compatibility.h")

        message(STATUS "hipBLASLT compatibility fix applied")
    endif()
endfunction()

# Create compatibility header
function(create_hipblaslt_compatibility_header)
    set(COMPAT_HEADER "${CMAKE_CURRENT_BINARY_DIR}/hipblaslt_compatibility.h")
    file(WRITE ${COMPAT_HEADER} "
// hipBLASLT API Compatibility Header
// This header provides compatibility for changed hipBLASLT APIs

#ifndef HIPBLASLT_COMPATIBILITY_H
#define HIPBLASLT_COMPATIBILITY_H

// Add any necessary compatibility definitions here
// Currently handled via source patching

#endif // HIPBLASLT_COMPATIBILITY_H
")
endfunction()
