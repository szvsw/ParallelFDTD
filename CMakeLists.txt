CMAKE_MINIMUM_REQUIRED(VERSION 2.8)
#The name of the project
project(parallelFDTD)


# These compiler options are needed for compatibility with the Anaconda
# boost library and CUDA, which requires gcc-8.
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -DBOOST_SYSTEM_NO_LIB -std=gnu++11 -fPIC")


# Compile position independent code for the libarary
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -fPIC")


# Add Voxelizer, either building from github or if VOXELIZER_ROOT
# is given, use installation in that location
if(NOT VOXELIZER_ROOT)

  include(ExternalProject)
  ExternalProject_Add(Voxelizer
    GIT_REPOSITORY https://github.com/AaltoRSE/Voxelizer.git
    CMAKE_ARGS "-DCUDA_GENCODE=${CUDA_GENCODE}"
  )
  set( VOXELIZER_ROOT ${CMAKE_CURRENT_BINARY_DIR}/Voxelizer-prefix/src/Voxelizer )
  set( VOXELIZER_INCLUDE_DIR ${CMAKE_CURRENT_BINARY_DIR}/Voxelizer-prefix/src/ )
  set( VOXELIZER_LIB_PATH ${CMAKE_CURRENT_BINARY_DIR}/Voxelizer-prefix/src/Voxelizer-build/lib/ )

else()

  # The sources refer to Voxelizer includes as Voxelizer/include/...
  # Since one of the headers is common.h, maybe it's best to disambiguate.
  set( VOXELIZER_INCLUDE_DIR ${VOXELIZER_ROOT}/../ )
  set( VOXELIZER_LIB_PATH ${VOXELIZER_ROOT}/lib )

endif()

# Set the library name (cannot use find_package before it's compiled)
if(WIN32)
  set( VOXELIZER_LIB ${VOXELIZER_LIB_PATH}/Voxelizer.lib )
elseif(UNIX)
  set( VOXELIZER_LIB ${VOXELIZER_LIB_PATH}/libVoxelizer.a )
endif()



# Set default variables
set( GENERATE_DOXYGEN_DOCS OFF )
set( Boost_USE_STATIC_LIBS ON )
set( Boost_USE_MULTITHREADED ON )
set( Boost_USE_STATIC_RUNTIME OFF )


# Check if we are in a conda environment and find boost there
if(NOT "$ENV{CONDA_PREFIX}" STREQUAL "")
  message( STATUS "CONDA_PREFIX $ENV{CONDA_PREFIX}")
  set( BOOST_ROOT "$ENV{CONDA_PREFIX}" )
  set( Boost_NO_SYSTEM_PATHS ON )
  set( Python_FIND_VIRTUALENV ONLY)
endif()

# Find CUDA and Python libraries
find_package( CUDA REQUIRED )

# if building for python2, enable python bindings
if(BUILD_PYTHON2)
  set( BUILD_PYTHON on)
endif()



# Find python and python libraries
find_package( Python REQUIRED)
find_package( PythonLibs REQUIRED)

# Find boost
# Check the boost version to figure out the format of the python library
#FIND_PACKAGE(Boost)
if(Boost_VERSION_MINOR LESS 67 )

  if(WIN32) # On windows include the chrono library
    message( STATUS "WIN 66")
    find_package( Boost 1.41 COMPONENTS system thread date_time unit_test_framework python chrono numpy REQUIRED)
  else()
    find_package( Boost 1.41 COMPONENTS system thread date_time unit_test_framework python numpy REQUIRED)
  endif()

else()

  # with boost > 1.66, we need to specify the python version.
  if(WIN32) # On windows include the chrono library
    find_package( Boost 1.41 COMPONENTS system thread date_time unit_test_framework python chrono numpy REQUIRED)
  else()
    find_package( Boost 1.41 COMPONENTS system thread date_time unit_test_framework python${Python_VERSION_MAJOR}${Python_VERSION_MINOR} numpy REQUIRED)
  endif()

endif()


if(Boost_USE_STATIC_RUNTIME)
  foreach(flag_var
          CMAKE_CXX_FLAGS CMAKE_CXX_FLAGS_DEBUG CMAKE_CXX_FLAGS_RELEASE
          CMAKE_CXX_FLAGS_MINSIZEREL CMAKE_CXX_FLAGS_RELWITHDEBINFO)
     if(${flag_var} MATCHES "/MD")
        string(REGEX REPLACE "/MD" "/MT" ${flag_var} "${${flag_var}}")
     endif(${flag_var} MATCHES "/MD")
  endforeach(flag_var)
endif()



# These are only needed for visualization
if(BUILD_VISUALIZATION)
  add_definitions(-DCOMPILE_VISUALIZATION)
  find_package( OpenGL REQUIRED )
  find_package( GLUT REQUIRED )
  find_package( GLEW REQUIRED )
else()
  set(GLUT_LIBRARIES "")
  set(OPENGL_LIBRARIES "")
  set(GLEW_LIBRARIES "")
endif()


# MAC and LINUX: explicitly use x11 GL
# If Cmake fails to find these, uncomment and edit the paths here
#
# Example directories for macports installs
#if(APPLE)
#  set(GLUT_INCLUDE_DIR /opt/X11/include/GL)
#  set(GLUT_glut_LIBRARY /opt/X11/lib/libglut.dylib)
#
#  link_directories(/opt/local/lib)
#  link_directories(/opt/x11/lib)
#endif()
#
# Cmake will find these
#if(UNIX)
#  find_library(GLEW_LIBRARIES libGLEW.so /usr/lib/x86_64-linux-gnu/)
#  link_directories(/usr/local/lib)
#  set( CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -w -m64 -fPIC -O3 -DBOOST_PYTHON_DYNAMIC_MODULE")
#  set(unix_specific_libraries pthread rt)
#endif()



# Set CUDA architecture
if(CUDA_GENCODE)
  set( CUDA_NVCC_FLAGS_RELEASE ${CUDA_NVCC_FLAGS_RELEASE};
                            -gencode ${CUDA_GENCODE}
                          )

  set( CUDA_NVCC_FLAGS_DEBUG ${CUDA_NVCC_FLAGS_DEBUG};
                            -gencode ${CUDA_GENCODE}
                          )
else()
  set( CUDA_NVCC_FLAGS_RELEASE ${CUDA_NVCC_FLAGS_RELEASE};
                         -gencode arch=compute_60,code=sm_70
                         -gencode arch=compute_61,code=sm_61
                         -gencode arch=compute_60,code=sm_60
                         -gencode arch=compute_52,code=sm_52
                         -gencode arch=compute_37,code=sm_37
                         )
  set( CUDA_NVCC_FLAGS_DEBUG ${CUDA_NVCC_FLAGS_DEBUG};
                        -gencode arch=compute_60,code=sm_70
                         -gencode arch=compute_61,code=sm_61
                         -gencode arch=compute_60,code=sm_60
                         -gencode arch=compute_52,code=sm_52
                         -gencode arch=compute_37,code=sm_37
                         )
endif()



# List C++ source files
set(SOURCES_CPP ${CMAKE_SOURCE_DIR}/src/base/GeometryHandler.cpp
                ${CMAKE_SOURCE_DIR}/src/base/MaterialHandler.cpp
                ${CMAKE_SOURCE_DIR}/src/base/SimulationParameters.cpp
                ${CMAKE_SOURCE_DIR}/src/base/SrcRec.cpp
                ${CMAKE_SOURCE_DIR}/src/io/FileReader.cpp
                ${CMAKE_SOURCE_DIR}/src/io/Image.cpp
                ${CMAKE_SOURCE_DIR}/src/App.cpp
                ${CMAKE_SOURCE_DIR}/src/logger.cpp )

if(BUILD_VISUALIZATION)
  set(SOURCES_CPP ${SOURCES_CPP} ${CMAKE_SOURCE_DIR}/src/gl/AppWindow.cpp
                                 ${CMAKE_SOURCE_DIR}/src/gl/AppPbo.cpp
                                 ${CMAKE_SOURCE_DIR}/src/gl/AppVbo.cpp
                                 ${CMAKE_SOURCE_DIR}/src/gl/glHelpers.cpp
                                 ${CMAKE_SOURCE_DIR}/src/base/cameraProto.cpp)
endif()

# List CUDA source files
set(SOURCES_CU ${CMAKE_SOURCE_DIR}/src/kernels/cudaUtils.cu
               ${CMAKE_SOURCE_DIR}/src/kernels/visualizationUtils.cu
               ${CMAKE_SOURCE_DIR}/src/kernels/voxelizationUtils.cu
               ${CMAKE_SOURCE_DIR}/src/kernels/cudaMesh.cu
               ${CMAKE_SOURCE_DIR}/src/kernels/kernels3d.cu )




include_directories( ${VOXELIZER_INCLUDE_DIR} )
include_directories(${CMAKE_SOURCE_DIR}/include)
include_directories( ${OPENGL_INCLUDE_DIR} )
include_directories( ${Boost_INCLUDE_DIRS} )
include_directories( ${GLUT_INCLUDE_DIR} )
include_directories( ${GLEW_INCLUDE_DIRS} )
include_directories( ${PYTHON_INCLUDE_DIRS} )

# Print some useful information
message( STATUS "CUDA root: ${CUDA_TOOLKIT_ROOT_DIR}")
message( STATUS "Voxelizer ROOT: ${VOXELIZER_ROOT}" )
message( STATUS "OpenGL include dir: ${OPENGL_INCLUDE_DIR}" )
message( STATUS "Boost include dir: ${Boost_INCLUDE_DIRS}" )
message( STATUS "GLUT include dir: ${GLUT_INCLUDE_DIR}" )
message( STATUS "GLEW include dirs: ${GLEW_INCLUDE_DIRS}" )
message( STATUS "Voxelizer include dir: ${VOXELIZER_INCLUDE_DIR}" )
message( STATUS "Python: ${PYTHON_INCLUDE_DIRS}" )

message( STATUS "GLUT lib: ${GLUT_glut_LIBRARY}" )
message( STATUS "OpenGL lib: ${OPENGL_gl_LIBRARY}" )
message( STATUS "Boost lib: ${Boost_LIBRARIES}" )
message( STATUS "Boost python lib: ${Boost_PYTHON_LIBRARY}" )
message( STATUS "GLEW libs: ${GLEW_LIBRARIES}" )
message( STATUS "Voxelizer lib: ${VOXELIZER_LIB}" )
message( STATUS "Python lib: ${PYTHON_LIBRARIES}" )

message( STATUS "CMAKE_C_COMPILER_VERSION : ${CMAKE_C_COMPILER_VERSION}" )
message( STATUS "CMAKE_CXX_COMPILER_VERSION : ${CMAKE_CXX_COMPILER_VERSION}" )

message( STATUS "Doxygen ${GENERATE_DOXYGEN_DOCS}")


# Include the source directory
add_subdirectory(src)

if(BUILD_TESTS)
  # and the test directory
  add_subdirectory(tests)
endif()

if ( GENERATE_DOXYGEN_DOCS )
  # also build documentition
  add_subdirectory( doc )
endif ()
