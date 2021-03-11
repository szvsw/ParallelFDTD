Parallel FDTD
=============

An FDTD solver for room acoustics using CUDA. To reference this code:

Saarelma, J. and Savioja, L., An open source finite-difference time-domain solver for room acoustics using graphics processing units. Forum Acusticum, Krakow, Poland, Sept. 2014

Installation
=============

## Dependencies

> ### On the Aalto Triton cluster
>
> Load the dependencies with `module load anaconda gcc/6.5.0 cuda matlab/r2019b`.
> You also need to create the anaconda environment, see below.
>


### Must be installed on system
- Anaconda (https://docs.anaconda.com/anaconda/install/) or Miniconda (https://docs.conda.io/en/latest/miniconda.html)
- CUDA 5-10, tested on compute capability 3.0 - 6.1

If visualization is compiled (set 'BUILD_VISUALIZATION' cmake flag - see below):
- Freeglut,  http://freeglut.sourceforge.net/ , Accessed May 2014  
- GLEW, tested on 1.9.0, http://glew.sourceforge.net/, Accessed May 2014  

For Matlab bindings:
- Matlab r2019b.

### For MPI execution
- HDF5 libraries (install with `conda`, see below)
- HDF5 for python (install with `conda`, see below)


### Installed through Anaconda
These are most easily installed through Anaconda, following the instructions
below. Alternatively they can be installed manually. In that case skip the
`conda` commands in installation instructions.
- Boost Libraries, tested on 1.75,  https://www.boost.org/users/history/version_1_75_0.html, Accessed January 2021
- Python 2.7 or 3 (For the python interface)
- NumPy, SciPy (For the python interface)



# Python

## Installation

The python bindings can be installed through pip. First you need to install the
dependencies mentioned above. Then create a conda environment for your
installation with the command
```
1.1 conda create -n PFDTD -c conda-forge boost py-boost cmake numpy scipy
1.2 conda activate PFDTD
```

Now you can install the package using
```
1.3 pip install git+https://github.com/AaltoRSE/ParallelFDTD.git
```

This will use cmake to compile the library and build the python package. The
whole process can take a while. If you wish to know more about what the
installer is doing, add `-v` to the command.

## Usage

In the end of the installation library is now installed into the anaconda
environment. To use it, you need to activate the environment.
```
1.4 conda activate PFDTD
```

Now you can import the package in your python code with
```
1.5 import pyParallelFDTD
```

For more details see the example in [python/testBench.py](python/testBench.py). The script uses two
additional packages, `matplotlib` and `h5py`. You can install these using
```
1.6 conda install -c conda-forge matplotlib h5py
```

> ### Python 2
>
> To build for Python 2.7, create the environment with
> ```
> conda create -n PFDTD -c conda-forge boost py-boost cmake python=2.7
> ```
>
> Python 2 is no longer developed and supporting it will not be possible
> for long.



# Matlab and C++

## Compiling

The compilation has been tested on:
- CentOS 6, CentOS 7 with GCC 8.5.0
- Windows 7, Windows 10 with vc120, vc140 compilers
- Triton, the Aalto University cluster


### 1. Download and install the dependencies  

The Boost library versions are handled most easily using Anaconda. Install
it first following the instructions at
https://docs.anaconda.com/anaconda/install/ (or install miniconda,
https://docs.conda.io/en/latest/miniconda.html)

Clone this repository. In the cloned folder create the Conda environment using
(you can replace the environment name `PFDTD` with your own preference)
```
1.1 git clone git@github.com:AaltoRSE/ParallelFDTD.git
1.2 cd ParallelFDTD
1.3 conda env create -n PFDTD -f conda_environment.yml
```

This will install compatible versions Boost and cmake into a new conda evironment.

Activate the new environment
```
1.4 conda activate PFDTD
```

### 2. Build ParallelFDTD with CMAKE

```
4.1 go to the folder of the repository
4.2 mkdir build
4.3 cd build
```

#### WINDOWS

Open a VSxxxx (x64) Native Tools command prompt and follow the instructions:

```
4.4 cmake -G"NMake Makefiles" -DCMAKE_BUILD_TYPE=release -DBUILD_MATLAB=on ../  
4.5 nmake  
4.6 nmake install
```

#### Ubuntu / CentOS

```
4.4 cmake -DCMAKE_BUILD_TYPE=release -DBUILD_MATLAB=on ../
4.5 make
4.6 make install
```


### Other Options
> ### Voxelizer
>
> Cmake will compile and external dependency called Voxelizer. If you
> prefer to use your own installation, see the end of this document.

To build the Matlab bindings use `-DBUILD_MATLAB=on`.

You can set the CUDA compute capabilities and architectures using the
`-CUDA_GENCODE=` flag to the cmake command. For example to build only with
compute capability 6.1, use `-DCUDA_COMPUTE=arch=compute_61,code=sm_61`.
The default without this flag is to compile for set of architectures from 3.7
to 7.0, but using compute capability 6.1 for the architecture 7.0. This is
compatible with CUDA 10.2 and Nvidia GPUs up to Tesla V100.

To build the tests, python module (for linux only) and visualization, use the following flags. Real-time visualization is applicable only with a single GPU device. By default, the visualization is not compiled. The dependencies regarding the visualization naturally do not apply if compiled without the flag.
```
-DBUILD_TESTS=on
-DBUILD_VISUALIZATION=on
```
with the cmake command.


## Matlab Usage

The Matlab library (three mex files) have been copied to `ParallelFDTD/matlab`.
The directory also contains a test script, (matlab/testBench.m)[matlab/testBench.m], which you can also
use for reference. The next section contains more detail on using the library.



Practicalities
==============

In order to run a simulation, some practical things have to be done:

### Make a model of the space

One convenient software choice for building models for simulation is SketchUp Make: http://www.sketchup.com/. The software is free for non-commercial use, and has a handy plugin interface that allows the user to write ruby scripts for geometry modifications and file IO.

A specific requirement for the geometry is that it should be solid/watertight. In practice this means that the geometry can not contain single planes or holes. The geometry has to have a volume. For example, a balcony rail can not be represented with a single rectangle, the rail has to be drawn as a box, or as a volume that is part of the balcony itself. The reason for this is that the voxelizer makes intersection tests in order to figure out whether a node it is processing is inside or outside of the geometry. Therefore, a plane floating inside a solid box will skrew this calculation up hence after intersecting this floating plane, the voxelizer thinks it has jumped out of the geometry, when actually it is inside. A hole in the geometry will do the opposite; if the voxelizer hits a hole in the boundary of the model, it does not know it is outside regardless  of the intentions of the creator of the model. A volume inside a volume is fine.

A couple of tricks/tools to check the model:
- In SketchUp, make a "Group" (Edit -> Make Group) out of the geometry you want to export, check the "Entity info" window (if not visible: Window -> Entity info). If the entity info shows a volume for your model, it should be useable with ParallelFDTD. (Thanks for Alex Southern for this trick).
- IF the entity info does not give you a volume, you need to debug your model. A good tool for this is "Solid Inspector" ( goo.gl/I4UcS6 ), with which you can track down holes and spare planes and edges from the model.


When the geometry has been constructed, it has to be exported to more simple format in order to import it to Matlab. For this purpose a JSON exported is provided. The repository contains a rubyscript plugin for SketchUp in the file:

```
geom2json.rb
```

Copy this file to the sketchup Plugins Folder. The plugin folder of the application varies depending on the operating system. Best bet is to check from the SketchUp help website http://help.sketchup.com/en/article/38583 (Accessed 5.9.2014). After installing the plugin and restarting SketchUp, an option "Export to JSON" under the "Tools" menu should have appeared. Now by selecting all the surfaces of the geometry which are to be exported and executing this command, a "save as" dialogue should appear.

### Import the geometry to Matlab
The simulation tool does not rely on any specific CAD format. Any format which you have a Matlab importer available and that has the geometry described as list of vertices coordinates and triangle indices should do. As mentioned above, a requirement for the geometry is that it is solid/watertight. The format that is supported right away is JSON file that contains the vertice coordinates and triangle indices. Layer information is also really convenient for assigning materials for the model. JSON parser for Matlab (JSONlab by Qianqian Fang goo.gl/v2jnHx) is included in this repository.

### Run the simulation
The details of running simulations are reviewed in the scripts matlab/testBench.m for matlab, and python/testBench.py for Python.




Installing Voxelizer manually
=============================

Clone the Voxelizer library from https://github.com/AaltoRSE/Voxelizer.git. Follow the installation instructions found there.

```
2.1 go to the folder of the repository  
2.2 mkdir build
2.3 cd build  
2.4 cmake ..
2.5 make  
```

If you will manually select CUDA compute capabilities for ParallelFDTD, also add
the `-DCUDA_COMPUTE` flag also here.

When compiling ParallelFDTD, add `-DVOXELIZER_ROOT=path_to_voxelizer` to the cmake command.
