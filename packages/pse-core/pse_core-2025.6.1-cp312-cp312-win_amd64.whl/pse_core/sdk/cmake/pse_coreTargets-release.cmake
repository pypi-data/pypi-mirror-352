#----------------------------------------------------------------
# Generated CMake target import file for configuration "Release".
#----------------------------------------------------------------

# Commands may need to know the format version.
set(CMAKE_IMPORT_FILE_VERSION 1)

# Import target "pse_core::pse_sdk" for configuration "Release"
set_property(TARGET pse_core::pse_sdk APPEND PROPERTY IMPORTED_CONFIGURATIONS RELEASE)
set_target_properties(pse_core::pse_sdk PROPERTIES
  IMPORTED_LINK_INTERFACE_LANGUAGES_RELEASE "CXX"
  IMPORTED_LOCATION_RELEASE "${_IMPORT_PREFIX}/pse_core/sdk/lib/pse_sdk.lib"
  )

list(APPEND _cmake_import_check_targets pse_core::pse_sdk )
list(APPEND _cmake_import_check_files_for_pse_core::pse_sdk "${_IMPORT_PREFIX}/pse_core/sdk/lib/pse_sdk.lib" )

# Commands beyond this point should not need to know the version.
set(CMAKE_IMPORT_FILE_VERSION)
