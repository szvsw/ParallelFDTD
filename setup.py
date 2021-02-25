import setuptools
import os
import shutil
import subprocess

from setuptools import Extension
from setuptools.command.build_py import build_py
from setuptools.command.build_ext import build_ext
from setuptools.command.install_lib import install_lib

PACKAGE_NAME = 'pyParallelFDTD'


class CMakeExtension(Extension):
    def __init__(self, name, sources=[], libraries=[]):
        super().__init__(name, sources, libraries=libraries)
        self.sourcedir = os.path.abspath(".")


class InstallCMakeLibs(install_lib):
    def run(self):
        self.distribution.data_files = []

        # make sure the cmake command is run
        self.run_command('build_ext')
        self.run_command('build_py')

        library_dir = self.distribution.cmake_build_dir
        library_dir = os.path.join(library_dir, 'python')
        build_dir = os.path.join(self.build_dir, PACKAGE_NAME)
        print(build_dir)
        print(library_dir)

        # check files in the binary directory and copy any libraries
        # This is a bit more general than we need, but it solves the problem
        # of different file extensions in Unix and Windows
        for filename in os.listdir(library_dir):
            print(library_dir, filename)
            # check if the file is a library
            if (os.path.isfile(os.path.join(library_dir, filename)) and
                os.path.splitext(filename)[1] in [".dll", ".so"]):
               libname = os.path.join(library_dir, filename)

               # build_dir seems to be where the package folder goes
               dist_path = os.path.join(build_dir)
               dist_name = os.path.join(dist_path, filename)

               print(libname, dist_path, dist_name)
               shutil.copy(libname, dist_path)

               self.distribution.data_files.append(dist_name)

        super().run()

    def get_outputs(self):
        return self.distribution.data_files


class CMakeBuild(build_ext):
    def run(self):
        # Check that Cmake is installed
        try:
            subprocess.check_output(["cmake", "--version"])
        except (OSError, subprocess.SubprocessError):
            raise RuntimeError(
                "Cannot find Cmake. Please install Cmake before continuing."
            )
        # Run the build command. The build_ext class contains a list
        # of buildable extentions. There should be only one, but
        # run through the whole list for compatiblity
        for ext in self.extensions:
            self.build_extension(ext)
        super().run()

    def build_extension(self, ext):
        cmake_config = ["-DBUILD_PYTHON=on"]
        build_config = ["-j", "4"]

        self.distribution.cmake_build_dir = self.build_temp

        # Create the build directory if necessary
        if not os.path.exists(self.build_temp):
            os.makedirs(self.build_temp)

        # Run the Cmake command
        subprocess.check_call(
          ["cmake", f"-H{ext.sourcedir}", f"-B{self.build_temp}"] +
          cmake_config
        )

        # Build and install
        subprocess.check_call(
          ["cmake", "--build", self.build_temp, '-t', 'libPyFDTD', '--'] +
          build_config
        )
        #subprocess.check_call(
        #  ["cmake", "--install", self.build_temp]
        #)


setuptools.setup(
    name=PACKAGE_NAME,
    version='0.0',
    description="Python bindings to ParallelFDTD",
    url="https://github.com/AaltoRSE/ParallelFDTD",
    license="MIT License",
    packages=[
        PACKAGE_NAME,
    ],
    package_dir={
        PACKAGE_NAME: 'dist/libPyFDTD',
    },
    package_data={'pyParallelFDTD': ['liblibPyFDTD.so']},
    ext_modules=[
        CMakeExtension(PACKAGE_NAME+".liblibPyFDTD", libraries='liblibPyFDTD.so'),
    ],
    cmdclass={
      'build_ext': CMakeBuild,
      'install_lib': InstallCMakeLibs,
    },
)
