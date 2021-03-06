import os

from conans import ConanFile, CMake, tools

class LibgeotiffConan(ConanFile):
    name = "libgeotiff"
    description = "Libgeotiff is an open source library normally hosted on top " \
                  "of libtiff for reading, and writing GeoTIFF information tags."
    license = ["MIT", "BSD-3-Clause"]
    topics = ("conan", "libgeotiff", "geotiff", "tiff", "parser")
    homepage = "https://github.com/OSGeo/libgeotiff"
    url = "https://github.com/conan-io/conan-center-index"
    exports_sources = ["CMakeLists.txt", "patches/**"]
    generators = "cmake", "cmake_find_package_multi"
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}

    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.cppstd
        del self.settings.compiler.libcxx

    def requirements(self):
        self.requires("libtiff/4.1.0")
        self.requires("proj/7.1.0")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename(self.name + "-" + self.version, self._source_subfolder)

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        cmake = self._configure_cmake()
        cmake.build()

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["WITH_UTILITIES"] = False
        self._cmake.definitions["WITH_TIFF"] = True
        self._cmake.definitions["WITH_ZLIB"] = False # zlib and libjpeg are not direct
        self._cmake.definitions["WITH_JPEG"] = False # dependencies of libgeotiff
        self._cmake.definitions["WITH_TOWGS84"] = True
        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def package(self):
        self.copy("LICENSE", dst="licenses", src=os.path.join(self._source_subfolder, "libgeotiff"))
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "cmake"))
        tools.rmdir(os.path.join(self.package_folder, "doc"))
        tools.rmdir(os.path.join(self.package_folder, "share"))

    def package_info(self):
        # TODO: CMake imported target shouldn't be namespaced (geotiff_library instead of GeoTIFF::geotiff_library)
        self.cpp_info.names["cmake_find_package"] = "GeoTIFF"
        self.cpp_info.names["cmake_find_package_multi"] = "GeoTIFF"
        self.cpp_info.components["geotiff"].names["cmake_find_package"] = "geotiff_library"
        self.cpp_info.components["geotiff"].names["cmake_find_package_multi"] = "geotiff_library"
        self.cpp_info.components["geotiff"].libs = tools.collect_libs(self)
        if self.settings.os == "Linux":
            self.cpp_info.components["geotiff"].system_libs.append("m")
        self.cpp_info.components["geotiff"].requires = ["libtiff::libtiff", "proj::proj"]
