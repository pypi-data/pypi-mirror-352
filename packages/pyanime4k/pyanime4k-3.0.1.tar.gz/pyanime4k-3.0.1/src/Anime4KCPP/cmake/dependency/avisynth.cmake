if(NOT TARGET dep::avisynth)
    add_library(dep_avisynth INTERFACE IMPORTED)
    find_path(dep_avisynth_INCLUDE
        NAMES avisynth.h
        PATHS
            "C:/Program Files (x86)/AviSynth+/FilterSDK/include"
            "C:/Program Files/AviSynth+/FilterSDK/include"
    )
    if(dep_avisynth_INCLUDE)
        target_include_directories(dep_avisynth INTERFACE ${dep_avisynth_INCLUDE})
    else()
        message(STATUS "dep: avisynth not found, will be fetched online.")
        include(FetchContent)
        FetchContent_Declare(
            avisynth
            GIT_REPOSITORY https://github.com/AviSynth/AviSynthPlus.git
            GIT_TAG master
            SOURCE_SUBDIR do_not_find_cmake # To make sure CMakeLists.txt won't run
        )
        FetchContent_MakeAvailable(avisynth)
        target_include_directories(dep_avisynth INTERFACE $<BUILD_INTERFACE:${avisynth_SOURCE_DIR}/avs_core/include>)
    endif()
    add_library(dep::avisynth ALIAS dep_avisynth)
endif()
