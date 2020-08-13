cmake_minimum_required(VERSION 3.1)
project(test_package C)

set(CMAKE_VERBOSE_MAKEFILE TRUE)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

find_package(GeoTIFF REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.c)
target_link_libraries(${PROJECT_NAME} ${CONAN_LIBS}) # TODO: replace by non-namespaced target as soon as conanfile is fixed
