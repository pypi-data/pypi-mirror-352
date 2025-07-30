cmake_minimum_required(VERSION 3.24)

project(sear C CXX ASM)
set(CXX_STANDARD 14)

option(SEAR_ENABLE_PYTHON "Enables building the Python language module." OFF)

add_subdirectory(externals)

find_package(OpenSSL REQUIRED)
find_library(ZOSLIB libzoslib.a REQUIRED)

add_library(
    sear

    sear/irrsdl00/irrsdl00.cpp
    sear/irrsdl00/keyring_extractor.cpp
    sear/irrsdl00/keyring_modifier.cpp
    sear/irrsdl00/keyring_post_processor.cpp

    sear/irrseq00/irrseq00.s
    sear/irrseq00/profile_extractor.cpp
    sear/irrseq00/profile_post_processor.cpp

    sear/irrsmo00/irrsmo00_error.cpp
    sear/irrsmo00/irrsmo00.cpp
    sear/irrsmo00/xml_generator.cpp
    sear/irrsmo00/xml_parser.cpp

    sear/key_map/key_map.cpp
    sear/validation/trait_validation.cpp
    sear/logger.cpp
    sear/sear_error.cpp
    sear/sear.cpp
    sear/security_admin.cpp
    sear/security_request.cpp
)
target_include_directories(
    sear PUBLIC
    sear
    sear/irrsdl00
    sear/irrseq00
    sear/irrsmo00
    sear/key_map
    sear/validation
    # add generated header to include path
    "${CMAKE_CURRENT_BINARY_DIR}/sear"
)
target_compile_definitions(sear PUBLIC _POSIX_C_SOURCE=200112L)

# embed json schema into sear_schema.hpp
file(READ schema.json SEAR_SCHEMA)
configure_file(sear/sear_schema.hpp.in sear/sear_schema.hpp)

target_link_libraries(sear PRIVATE nlohmann_json::nlohmann_json nlohmann_json_schema_validator OpenSSL::SSL "${ZOSLIB}")

if (SEAR_ENABLE_PYTHON)
    find_package(Python3 REQUIRED COMPONENTS Development Development.SABIModule)

    Python3_add_library(pysear MODULE USE_SABI 3.12 sear/python/_sear.c)
    target_link_libraries(pysear PRIVATE sear Python3::Python)

    if (DEFINED SEAR_PYTHON_EXTENSION_PATH)
        message(STATUS "Installing Python module to: ${SEAR_PYTHON_EXTENSION_PATH}")
        cmake_path(GET SEAR_PYTHON_EXTENSION_PATH FILENAME MODULE_FILENAME)
        cmake_path(GET SEAR_PYTHON_EXTENSION_PATH PARENT_PATH MODULE_DIR)
        install(PROGRAMS "$<TARGET_FILE:pysear>" DESTINATION "${MODULE_DIR}" RENAME "${MODULE_FILENAME}")
    endif()
endif()
