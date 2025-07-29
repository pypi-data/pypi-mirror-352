import shutil
from setuptools import setup, Extension
from setuptools.command.build_ext import build_ext
import os
import subprocess
import sys
import platform

class CMakeExtension(Extension):
    def __init__(self, name, sourcedir=''):
        super().__init__(name, sources=[])
        self.sourcedir = os.path.abspath(sourcedir)

class CMakeBuild(build_ext):
    def run(self):
        for ext in self.extensions:
            self.build_extension(ext)

    def build_extension(self, ext):
        extdir = os.path.abspath(os.path.dirname(self.get_ext_fullpath(ext.name)))
        cmake_args = [
            f'-DCMAKE_LIBRARY_OUTPUT_DIRECTORY={extdir}',
            f'-DPYTHON_EXECUTABLE={sys.executable}',
            '-DCMAKE_OSX_DEPLOYMENT_TARGET=10.9',
            '-DCMAKE_BUILD_TYPE=Release'
        ]

        if platform.system() == "Darwin":
            cmake_args += ['-DCMAKE_OSX_ARCHITECTURES=x86_64']

        build_args = ['--config', 'Release']
        build_temp = os.path.join(self.build_temp, ext.name)
        os.makedirs(build_temp, exist_ok=True)

        print("源代码目录:", ext.sourcedir)
        print("构建目录:", build_temp)
        print("CMake参数:", cmake_args)
        print("构建参数:", build_args)

        # 执行 CMake 构建
        subprocess.check_call(['cmake', ext.sourcedir] + cmake_args, cwd=build_temp)
        subprocess.check_call(['cmake', '--build', '.'] + build_args, cwd=build_temp)

        # === 拷贝 libspine.dylib 到 src/cpyne ===
        lib_name = "libspine.dylib"
        compiled_lib_path = os.path.join(extdir, lib_name)
        package_lib_path = os.path.join("src", "cpyne", lib_name)

        if os.path.exists(compiled_lib_path):
            os.makedirs(os.path.dirname(package_lib_path), exist_ok=True)
            print("Copying", compiled_lib_path, "→", package_lib_path)
            shutil.copy(compiled_lib_path, package_lib_path)
        else:
            print("构建后未找到动态库:", compiled_lib_path)
            raise FileNotFoundError(compiled_lib_path)


setup(
    name='cpyne',
    version='0.2.0',
    author='GrillingUXO',
    description='Python bindings for Spine Runtime using ctypes',
    ext_modules=[CMakeExtension('spine-c', sourcedir='src/spine-c')],
    cmdclass={'build_ext': CMakeBuild},
    packages=['cpyne'],
    package_dir={'': 'src'},
    python_requires='>=3.9.7',
    include_package_data=True,
    zip_safe=False
)
