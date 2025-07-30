from pathlib import Path

from setuptools import Extension, setup
from setuptools.command.build_ext import build_ext as _build_ext
from wheel.bdist_wheel import bdist_wheel as _bdist_wheel


class CMakeExtension(Extension):
    def __init__(self, name):
        # don't invoke the original build_ext for this special extension
        super().__init__(name, sources=[])


class bdist_wheel(_bdist_wheel): # noqa: N801
    def finalize_options(self):
        super().finalize_options()

        # marks built wheels as 'none-any' to allow installation on non-z/OS systems
        self.root_is_pure = True


class build_ext(_build_ext): # noqa: N801
    def build_extension(self, ext) -> None:
        self.build_cmake(ext)

    def build_cmake(self, ext):
        build_temp = Path(self.build_temp)
        # ensure temporary build directory exists
        build_temp.mkdir(parents=True, exist_ok=True)

        extdir = Path(self.get_ext_fullpath(ext.name))
        # ensure output directory exists
        # probably not necessary, as cmake will create the directory during install
        extdir.parent.mkdir(parents=True, exist_ok=True)

        build_lib = Path(self.build_lib)
        relative = extdir.relative_to(build_lib)

        config = 'Debug' if self.debug else 'Release'

        cmake_args = [
            "--preset", "zos-pysear",
            "-DSEAR_PYTHON_EXTENSION_PATH=" + str(relative),
            "-DCMAKE_BUILD_TYPE=" + config,
        ]

        build_args = [
            "--preset", "zos-pysear",
            '--config', config,
            '--', '-j4',
        ]

        install_args = [
            # cmake --install does not work with --preset (yet)
            # so build directory must be specified manually
            "build/zos-pysear",
            "--prefix=" + str(build_lib.absolute()),
        ]

        # configure cmake build directory
        self.spawn(['cmake'] + cmake_args)
        if not self.dry_run:
            # first run
            self.spawn(['cmake', '--build'] + build_args)
            # then install built extension module
            self.spawn(["cmake", "--install"] + install_args)


setup(
    name='pysear',
    ext_modules=[CMakeExtension('sear._C')],
    cmdclass={
        'build_ext': build_ext,
        "bdist_wheel": bdist_wheel,
    },
)
