#----------------------------------------------------------------
# Generated CMake target import file for configuration "Release".
#----------------------------------------------------------------

# Commands may need to know the format version.
set(CMAKE_IMPORT_FILE_VERSION 1)

# Import target "BSplineLib::utilities" for configuration "Release"
set_property(TARGET BSplineLib::utilities APPEND PROPERTY IMPORTED_CONFIGURATIONS RELEASE)
set_target_properties(BSplineLib::utilities PROPERTIES
  IMPORTED_LINK_INTERFACE_LANGUAGES_RELEASE "CXX"
  IMPORTED_LOCATION_RELEASE "${_IMPORT_PREFIX}/lib/static/libutilities.a"
  )

list(APPEND _cmake_import_check_targets BSplineLib::utilities )
list(APPEND _cmake_import_check_files_for_BSplineLib::utilities "${_IMPORT_PREFIX}/lib/static/libutilities.a" )

# Import target "BSplineLib::parameter_spaces" for configuration "Release"
set_property(TARGET BSplineLib::parameter_spaces APPEND PROPERTY IMPORTED_CONFIGURATIONS RELEASE)
set_target_properties(BSplineLib::parameter_spaces PROPERTIES
  IMPORTED_LINK_INTERFACE_LANGUAGES_RELEASE "CXX"
  IMPORTED_LOCATION_RELEASE "${_IMPORT_PREFIX}/lib/static/libparameter_spaces.a"
  )

list(APPEND _cmake_import_check_targets BSplineLib::parameter_spaces )
list(APPEND _cmake_import_check_files_for_BSplineLib::parameter_spaces "${_IMPORT_PREFIX}/lib/static/libparameter_spaces.a" )

# Import target "BSplineLib::vector_spaces" for configuration "Release"
set_property(TARGET BSplineLib::vector_spaces APPEND PROPERTY IMPORTED_CONFIGURATIONS RELEASE)
set_target_properties(BSplineLib::vector_spaces PROPERTIES
  IMPORTED_LINK_INTERFACE_LANGUAGES_RELEASE "CXX"
  IMPORTED_LOCATION_RELEASE "${_IMPORT_PREFIX}/lib/static/libvector_spaces.a"
  )

list(APPEND _cmake_import_check_targets BSplineLib::vector_spaces )
list(APPEND _cmake_import_check_files_for_BSplineLib::vector_spaces "${_IMPORT_PREFIX}/lib/static/libvector_spaces.a" )

# Import target "BSplineLib::splines" for configuration "Release"
set_property(TARGET BSplineLib::splines APPEND PROPERTY IMPORTED_CONFIGURATIONS RELEASE)
set_target_properties(BSplineLib::splines PROPERTIES
  IMPORTED_LINK_INTERFACE_LANGUAGES_RELEASE "CXX"
  IMPORTED_LOCATION_RELEASE "${_IMPORT_PREFIX}/lib/static/libsplines.a"
  )

list(APPEND _cmake_import_check_targets BSplineLib::splines )
list(APPEND _cmake_import_check_files_for_BSplineLib::splines "${_IMPORT_PREFIX}/lib/static/libsplines.a" )

# Import target "BSplineLib::input_output" for configuration "Release"
set_property(TARGET BSplineLib::input_output APPEND PROPERTY IMPORTED_CONFIGURATIONS RELEASE)
set_target_properties(BSplineLib::input_output PROPERTIES
  IMPORTED_LINK_INTERFACE_LANGUAGES_RELEASE "CXX"
  IMPORTED_LOCATION_RELEASE "${_IMPORT_PREFIX}/lib/static/libinput_output.a"
  )

list(APPEND _cmake_import_check_targets BSplineLib::input_output )
list(APPEND _cmake_import_check_files_for_BSplineLib::input_output "${_IMPORT_PREFIX}/lib/static/libinput_output.a" )

# Commands beyond this point should not need to know the version.
set(CMAKE_IMPORT_FILE_VERSION)
