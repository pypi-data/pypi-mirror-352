enable_language(CUDA)

set(CMAKE_CUDA_STANDARD 17)
set(CMAKE_CUDA_STANDARD_REQUIRED ON)
set(CMAKE_CUDA_EXTENSIONS OFF)
# 61-real for tesla p4, p40
set(CMAKE_CUDA_ARCHITECTURES 50-virtual 61-real CACHE STRING "CUDA architectures" FORCE)

if(NOT TARGET dep::cuda)
    find_package(CUDAToolkit REQUIRED)
    add_library(dep_cuda INTERFACE)
    target_link_libraries(dep_cuda INTERFACE CUDA::cudart_static)
    if((CMAKE_CXX_COMPILER_ID MATCHES "MSVC" OR (CMAKE_CXX_COMPILER_ID MATCHES "Clang" AND CMAKE_CXX_SIMULATE_ID MATCHES "MSVC" AND CMAKE_CXX_COMPILER_FRONTEND_VARIANT MATCHES "MSVC")) AND NOT AC_ENABLE_STATIC_CRT) #suppress warning
        target_link_options(dep_cuda INTERFACE /NODEFAULTLIB:LIBCMT)
    endif()
    add_library(dep::cuda ALIAS dep_cuda)
endif()
