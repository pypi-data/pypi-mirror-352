# build configuration for bundled external dependencies

# nlohmann json
# https://github.com/nlohmann/json
add_library(json INTERFACE)
target_include_directories(json INTERFACE "${CMAKE_CURRENT_SOURCE_DIR}/json")
add_library(nlohmann_json::nlohmann_json ALIAS json)

# json-schema-validator
# https://github.com/pboettch/json-schema-validator
add_library(
    nlohmann_json_schema_validator
    json-schema-validator/json-patch.cpp
    json-schema-validator/json-schema-draft7.json.cpp
    json-schema-validator/json-uri.cpp
    json-schema-validator/json-validator.cpp
    json-schema-validator/smtp-address-validator.cpp
    json-schema-validator/string-format-check.cpp
)
target_include_directories(nlohmann_json_schema_validator PUBLIC "${CMAKE_CURRENT_SOURCE_DIR}/json-schema-validator")
target_link_libraries(nlohmann_json_schema_validator PRIVATE json)
