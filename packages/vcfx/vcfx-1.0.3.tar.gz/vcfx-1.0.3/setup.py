# mypy: ignore-errors
import pathlib
import subprocess
import os
from setuptools import Extension, setup
from setuptools.command.build_ext import build_ext


def get_version():
    """Get version from VERSION file or environment variable."""
    # Try environment variable first
    env_version = os.environ.get("VCFX_VERSION")
    if env_version:
        return env_version

    # Try VERSION file
    version_file = pathlib.Path(__file__).parent / "VERSION"
    if version_file.exists():
        return version_file.read_text().strip()

    # Fallback
    return "0.0.0"


class CMakeExtension(Extension):
    def __init__(self, name):
        super().__init__(name, sources=[])


class CMakeBuild(build_ext):
    def build_extension(self, ext):
        extdir = pathlib.Path(self.get_ext_fullpath(ext.name)).parent.resolve()
        cmake_args = [
            f'-DCMAKE_LIBRARY_OUTPUT_DIRECTORY={extdir}',
            f'-DCMAKE_ARCHIVE_OUTPUT_DIRECTORY={extdir}',
            '-DPYTHON_BINDINGS=ON'
        ]
        build_temp = pathlib.Path(self.build_temp)
        build_temp.mkdir(parents=True, exist_ok=True)

        # Find the source directory - look for CMakeLists.txt
        source_dir = pathlib.Path(__file__).resolve().parent.parent

        # If we're in a temporary build directory, we need to find the original source
        if not (source_dir / "CMakeLists.txt").exists():
            # This might happen during wheel building from sdist
            # In this case, we should skip building the C++ extension
            print("Warning: CMakeLists.txt not found, building without C++ extension")
            return

        subprocess.check_call(
            ['cmake', str(source_dir)] + cmake_args,
            cwd=build_temp,
        )
        subprocess.check_call(
            ['cmake', '--build', '.', '--target', '_vcfx'],
            cwd=build_temp,
        )


setup(
    version=get_version(),
    packages=['vcfx', 'vcfx.tools'],
    package_dir={'vcfx': '.'},
    package_data={'vcfx': ['py.typed']},
    ext_modules=[CMakeExtension('vcfx._vcfx')],
    cmdclass={'build_ext': CMakeBuild},
    zip_safe=False,
    classifiers=[
        'Programming Language :: Python :: 3',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: POSIX :: Linux',
    ],
)
