
add_library( libParallelFDTD ${SOURCES_CPP} ${SOURCES_CU} )
add_executable( testExec main.cpp ${SOURCES_CPP} ${SOURCES_CU} )

if(BUILD_VOXELIZER)
  add_dependencies(libParallelFDTD Voxelizer)
  add_dependencies(testExec Voxelizer)
endif()

target_link_libraries(testExec ${GLUT_LIBRARIES}
                ${OPENGL_LIBRARIES} ${GLEW_LIBRARIES}
                ${VOXELIZER_LIB}
                ${Boost_LIBRARIES} ${unix_specific_libraries})

target_link_libraries( libParallelFDTD ${GLUT_LIBRARIES}
                  ${OPENGL_LIBRARIES} ${GLEW_LIBRARIES}
                  ${VOXELIZER_LIB}
                  ${Boost_THREAD_LIBRARY} ${Boost_SYSTEM_LIBRARY}
                  ${Boost_DATE_TIME_LIBRARY} ${unix_specific_libraries})


if(BUILD_PYTHON)
  add_library( libPyFDTD SHARED ${SOURCES_CPP} ${SOURCES_CU} ${CMAKE_SOURCE_DIR}/src/AppPy.cpp)
  if(BUILD_VOXELIZER)
    add_dependencies(libPyFDTD Voxelizer)
  endif()
  target_link_libraries( libPyFDTD ${GLUT_LIBRARIES} ${OPENGL_LIBRARIES}
        ${GLEW_LIBRARIES} ${VOXELIZER_LIB}  ${unix_specific_libraries}
        ${PYTHON_LIBRARIES} ${Boost_LIBRARIES}
  )
  set_target_properties( libPyFDTD PROPERTIES
    ARCHIVE_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/python/
    LIBRARY_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/python/
  )

  if(WIN32)
    if(NOT "$ENV{CONDA_PREFIX}" STREQUAL "")
      install(FILES ${CMAKE_BINARY_DIR}/python/liblibPyFDTD.lib DESTINATION $ENV{CONDA_PREFIX}/lib/python${Python_VERSION_MAJOR}.${Python_VERSION_MINOR}/)
    else()
      install(FILES ${CMAKE_BINARY_DIR}/python/liblibPyFDTD.lib DESTINATION ${CMAKE_SOURCE_DIR}/python/)
    endif()
  endif()
  if(UNIX)
    if(NOT "$ENV{CONDA_PREFIX}" STREQUAL "")
      install(FILES ${CMAKE_BINARY_DIR}/python/liblibPyFDTD.so DESTINATION $ENV{CONDA_PREFIX}/lib/python${Python_VERSION_MAJOR}.${Python_VERSION_MINOR}/)
    else()
      install(FILES ${CMAKE_BINARY_DIR}/python/liblibPyFDTD.so DESTINATION ${CMAKE_SOURCE_DIR}/python/)
    endif()
  endif()
endif()

set_target_properties( testExec PROPERTIES
   RUNTIME_OUTPUT_DIRECTORY ${CMAKE_SOURCE_DIR}/bin/
)
set_target_properties( libParallelFDTD PROPERTIES
   ARCHIVE_OUTPUT_DIRECTORY ${CMAKE_SOURCE_DIR}/lib/
   LIBRARY_OUTPUT_DIRECTORY ${CMAKE_SOURCE_DIR}/lib/
)

matlab_add_mex(NAME mem_check SRC ${CMAKE_SOURCE_DIR}/matlab/mem_check.cpp LINK_TO ${CUDA_cudart_static_LIBRARY} ${VOXELIZER_LIB} libParallelFDTD)
matlab_add_mex(NAME mex_FDTD SRC ${CMAKE_SOURCE_DIR}/matlab/mex_FDTD.cpp LINK_TO ${CUDA_cudart_static_LIBRARY} ${VOXELIZER_LIB} libParallelFDTD)
matlab_add_mex(NAME device_reset SRC ${CMAKE_SOURCE_DIR}/matlab/device_reset.cpp LINK_TO ${CUDA_cudart_static_LIBRARY} ${VOXELIZER_LIB} libParallelFDTD)

set_target_properties( mem_check PROPERTIES LIBRARY_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/Matlab/)
set_target_properties( mex_FDTD PROPERTIES LIBRARY_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/Matlab/)
set_target_properties( device_reset PROPERTIES LIBRARY_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/Matlab/)

install(FILES ${CMAKE_SOURCE_DIR}/src/base/cameraProto.hpp
              ${CMAKE_SOURCE_DIR}/src/base/GeometryHandler.h
              ${CMAKE_SOURCE_DIR}/src/base/MaterialHandler.h
              ${CMAKE_SOURCE_DIR}/src/base/SimulationParameters.h
              ${CMAKE_SOURCE_DIR}/src/base/SrcRec.h
              DESTINATION ${CMAKE_SOURCE_DIR}/matlab/includes/base/)


install(FILES ${CMAKE_SOURCE_DIR}/src/io/FileReader.h
              ${CMAKE_SOURCE_DIR}/src/io/Image.h
              DESTINATION ${CMAKE_SOURCE_DIR}/matlab/includes/io/)

install(FILES ${CMAKE_SOURCE_DIR}/src/kernels/cudaMesh.h
              ${CMAKE_SOURCE_DIR}/src/kernels/cudaUtils.h
              ${CMAKE_SOURCE_DIR}/src/kernels/kernels3d.h
              ${CMAKE_SOURCE_DIR}/src/kernels/visualizationUtils.h
              ${CMAKE_SOURCE_DIR}/src/kernels/voxelizationUtils.h
              DESTINATION ${CMAKE_SOURCE_DIR}/matlab/includes/kernels/)

install(FILES ${CMAKE_SOURCE_DIR}/src/math/geomMath.h
              ${CMAKE_SOURCE_DIR}/src/math/Matrix.h
              ${CMAKE_SOURCE_DIR}/src/math/Quaternion.h
              ${CMAKE_SOURCE_DIR}/src/math/Vector.h
              DESTINATION ${CMAKE_SOURCE_DIR}/matlab/includes/math/)


install(FILES ${CMAKE_SOURCE_DIR}/src/base/cameraProto.hpp
        DESTINATION ${CMAKE_SOURCE_DIR}/matlab/includes/base/)

install(FILES ${CMAKE_BINARY_DIR}/Matlab/device_reset.mexa64
              ${CMAKE_BINARY_DIR}/Matlab/mem_check.mexa64
              ${CMAKE_BINARY_DIR}/Matlab/mex_FDTD.mexa64
        DESTINATION ${CMAKE_SOURCE_DIR}/matlab/)
