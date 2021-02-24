import setuptools
from distutils.extension import Extension


setuptools.setup(
    name='pyParallelFDTD',
    version='0.0',
    description="Python bindings to ParallelFDTD",
    url="https://github.com/AaltoRSE/ParallelFDTD",
    license="MIT License",
    packages=[
        'pyParallelFDTD',
    ],
    package_dir={
        'pyParallelFDTD': 'dist/libPyFDTD',
    },
    package_data={'pyParallelFDTD': ['liblibPyFDTD.so']},
    #ext_modules=[
    #    Extension('pyParallelFDTD', ['dist/libPyFDTD/liblibPyFDTD.so'])
    #],
)
