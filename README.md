Parallel FDTD
=============

A FDTD solver for room acoustics using CUDA.


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



## Python Package

The python bindings can be installed through pip. First you need to install the
dependencies mentioned above. Then create a conda environment for your
installation with the command
```
1 conda create -n PFDTD -c conda-forge boost py-boost cmake
```

Now you can install the package using
```
2 pip install git+https://github.com/AaltoRSE/ParallelFDTD.git
```

This will use cmake to compile the library and build the python package. The
whole process can take a while. If you wish to know more about what the
installer is doing, add `-v` to the command.

> ### Python 2
>
> To build for Python 2.7, create the environment with
> ```
> conda create -n PFDTD -c conda-forge boost py-boost cmake python=2.7
> ```
>
> Python 2 is no longer developed and supporting it will not be possible
> for long.


## Compiling

Including Matlab bindings.

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
4.4 cmake -G"NMake Makefiles" -DCMAKE_BUILD_TYPE=release ../  
4.5 nmake  
4.6 nmake install
```

#### Ubuntu / CentOS

```
4.4 cmake -DCMAKE_BUILD_TYPE=release ../
4.5 make
4.6 make install
```

#### Options
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

You can also build the python bindings manually using `-DBUILD_PYTHON=on`.


### 3. Matlab

To build the Matlab bindings use `-DBUILD_MATLAB=on`.

The Matlab library (three mex files) have been copied to `ParallelFDTD/matlab`.
The directory also contains a test script, `testBench.m`, which you can also
use for reference. The next section contains more detail on using the library.



Basic Usage
===========

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


# Python

The steps above will install the `pyParallelFDTD` package.
In addition you need the `numpy` and `json` packages.
The geometry data is stored in the json format.
So first import the packages
```
import pyParallelFDTD as pf
import numpy as np
import json
```

Now you can load the geometry
```
file_stream = open("Data/box.json")
geometry = json.load(file_stream)
file_stream.close()
```

Parse the vertices from the `json` data.
```
vertices = np.reshape(m["vertices"], (int(np.size(m["vertices"])/3), 3))
indices = np.reshape(m["indices"], (int(np.size(m["indices"])/3), 3))
```

Next create a `pyParallelFDTD` app object and pass the geometry to it
```
app = pf.App()
app.initializeDevices()
app.initializeGeometryPy(indices.flatten().tolist(), vertices.flatten().tolist())
```

We'll set some other parameters here
```
app.setUpdateType(0)     # 0: SRL forward, 1: SRL sliced, 2: SRL centred
app.setNumSteps(2000)
app.setSpatialFs(100000)
app.setDouble(False)     # Use single precision
app.forcePartitionTo(1)
```

Next we will set the reflection coefficients of the surface materials. First we
will get surface layers from the data.
```
layer_list = m["layers_of_triangles"]
layer_names = m["layer_names"]
layers = {}
for k in range(0, len(layer_names)):
  layer_indices = [i for i, j in enumerate(layer_list) if j == layer_names[k]]
  layers[layer_names[k]] = layer_indices
```

What we actually need is admittance. Let's define two functions to map
reflection and absorption coefficients to admittance.
```
def reflection2Admittance(R):
    return (1.0-R)/(1.0+R)

def absorption2Admittance(alpha):
    return reflection2Admittance(np.sqrt(1.0-alpha))
```

We will set the reflection coefficients to 0.99
```
R_glob = 0.99
num_triangles = int(np.size(indices)/3)
num_coef = 20
materials = np.ones((num_triangles, num_coef))*reflection2Admittance(R_glob)
```

You can also set each layer separately
```
materials[layers['walls'], :] = reflection2Admittance(R_glob)
materials[layers['ceiling'], :] = reflection2Admittance(R_glob)
materials[layers['floor'], :] = reflection2Admittance(R_glob)
```

Now we can assign the materials to the model in the `pyParallelFDTD` app:
```
app.addSurfaceMaterials(materials.flatten().tolist(), num_triangles, num_coef)
```

We should also add a source
```
src_type = 0    # 0: Hard, 1: Soft, 2: Transparent
input_type = 1  # 0: Delta, 1: Gaussian, 2: Sine, 3: Given data
input_data_idx = 0
src = [0.5, 0.5, 0.5]
app.addSource(src[0], src[1], src[2], src_type, input_type, input_data_idx)
```

and some receivers
```
for i in range(0, np.shape(rec)[0]):
  app.addReceiver(rec[i][0],rec[i][1],rec[i][2])
```

We can now run a simulation using
```
app.runSimulation()
```

To get the results use
```
rec = [[0.6, 0.6, 0.6],
       [0.4, 0.4, 0.4]]

ret = []
for i in range(0, np.shape(rec)[0]):
  ret.append(np.array(app.getResponse(i)))
  # or ret.append(np.array(app.getResponseDouble(i))) for double precision
```

To turn this into a Numpy array and plot
```
ret = np.transpose(np.array(ret))
plt.plot(ret)
```

Finally, close the app
```
app.close()
del app
```

In addition to just running the simulation (`app.runSimulation()`), you can
visualize the simulation using
```
app.runVisualization()
```

or run captures
```
slice_n = 60
step = 100
orientation = 1

app.addSliceToCapture(slice_n, step, orientation)
app.runCapture()
```


# Matlab

To use ParallelFDTD from Matlab, follow the installation instructions in
the Compiling section below.

## Basic Usage

There are a number of useful functions in `matlab/functions`. First
make sure these are accessible.
```
addpath(genpath('functions'))
```

First let's assign some simulation parameters:
```
update_type = 0;     % 0: SRL forward, 1: SRL forward sliced 2: SRL centered
num_steps = 20000;
fs = 40000;
```

Which update to use is device dependent. SRL forward is most probably
the most efficient choice. SRL forward sliced might be faster with some
devices, and when using double precision. SRL centered is a bit of a
curiosity and definitely has the worst computational performance of the
choices.

The downside of SRL FDTD scheme which is used here, is the dispersion
error. The error is well known, and an interested reader should get
familiar with following publications [3][6]. A 10 time oversampling is
commonly used with the SRL scheme that results in ~2 % dispersion error.
An example, if a 1000 Hz band limit is to be achieved, the sampling
frequency of the domain should be 10,000 Hz.

Another downside of SRL scheme is that the simulation domain is a so
called staircase approximation. This can lead to a slight deviation of
the modes of the space. An interested reader can see [1].


We will force the App to use given number of partitions,
namely the number of devices.
Visualization will override this and use only one device.
```
force_partition_to = 1;
```

The selection of precision and the type of source has an effect on the stability
of the simulation [2]. As a guideline, double precision should be used
for simulation of impulse responses. For visualization purposes, single precision
is the only precision supported, and suffices for the purpose of
visualization of early reflections and scattering.

```
double_precision = 0;        % 0: single precision, 1: double precision
source_type = 1;             % 0: hard, 1: soft, 2: transparent
input_type = 3;              % 0: impulse, 1: gaussian, 2: sine, 3: given input data
input_data_idx = 0;
```

In the case of arbitrary input data, the input data vector index
`input_data_idx` has to be given for each source. The input data is
loaded later in this script.

Next we set up some sources. Sources have to be in shape of N X 6,
where N is the number of sources
```
src = [1.04, 0.56, 1.17, source_type, input_type, input_data_idx;
       2.24, 0.56, 1.17, source_type, input_type, input_data_idx;];

```

Receivers, shape N X 3
```
rec = [1.17, 3.24, 1.5;
       1.4, 3.24, 1.5];
```

We will not run visualization this time
```
visualization = 0;             % on: 1 or off: 0
```


Next we will load the geometry from a `json` file. Any format which is
possible to import to the workspace can be used. The end product after
parsing should be a list of vertex coordinates (in meters), and a list
of triangle indices defining the geometry. Triangle indices have to
start from 0.
```
m = loadjson('./Data/larun_hytti.json')
vertices = reshape(m.vertices, [3, length(m.vertices)/3])'; % N X 3 matrix
indices = reshape(m.indices, [3, length(m.indices)/3])'; % Number of triangles x 3 matrix
```

We will need to assign reflection coefficients to different layers
The materials are given as a [N x 20] matrix where
N is the number of the polygon/triangle in the geometry.
The format is slightly misleading, only one value is used from the
vector, namely the admittance of the selected "octave". The variable
octave indicates
which one of the values in the array is used. For example, value 0
fetches the
first value of the material vector at each triangle.

```
octave = 0;                     % Lets use the first "octave"
```

First set an uniform material
```
materials = ones(size(indices, 1), 20)*reflection2admitance(0.99); % Number of triangles x 20 coefficients
```

20 values is somewhat arbitrary number, which rationale is to
accommodate 2 variables per 10 octave bands
to be used in the calculation in future work.
Now only one variable is used, which is an admittance value

Next assign material to a layer
```
materials(strcmp(m.layers_of_triangles(:), 'ceiling'), :) = reflection2admitance(0.99);
materials(strcmp(m.layers_of_triangles(:), 'floor'), :) = reflection2admitance(0.99);
```

Next we need to set up some sources.
The input data should be in the shape [N, num_steps], where N is the
number of different input data vectors used in the simulation. Now,
two vectors are assigned, first one is a low pass filtered impulse, and
the second one a unprocessed impulse

```
src_data = zeros(2, num_steps);
src_data(:, 1) = 1;
b = fir1(100, 0.2);
src_data(1,:)= filter(b,1,src_data(1,:));
```

We also need to set up captures before running the simulation.
Captures of slices of the domain in certain time steps
size is Nx3, where N is the number of captures and the
three parameters given are [slice, step, orientation]

```
slice_capture = [];
mesh_captures = [];

captures = [];

%captures = [100, 1000, 0; ...
%            100, 1000, 1; ...
%            200, 1000, 2]
```

Captures of full domains in certain time steps. This functionality is
currently working with a single device only

```
mesh_captures = [100];
```

Finally we can run the simulation
```
P_rs = [];
[p mesh_r params] = runFDTD(single(vertices), ... // Vertices
                            indices, ... // Triangle indices
                            single(materials), ... // Material parameters in a format K X [r1, r2, .... r10, s1, s2, ..... s10]
                            single(src), ... % sources [N x 6]
                            single(rec), ...  % receivers [N x 3]
                            src_data, ... % Source input data
                            fs, ... % Sampling frequency of the mesh
                            num_steps, ... % Number of steps to run
                            visualization, ... % Run the visualization
                            captures, ...   % Assigned captures in the formant N X [slice, step, orientation]
                            update_type, ...
                            mesh_captures, ... % Mesh captures in a format M X [step to be captured]
                            double_precision, ... % 0: single prescision , 1: double precision
                            force_partition_to, ... % Number of partition / devices used
                            octave);  % Which value of material vector is used
                                      % (in default mode a number between
                                      % [0 , 20])
```

After the simulation we use the FDTDpostFilter function to get
the results
```
P_rs = resample(FDTDpostFilter(double(p), fs, 0.2), 48000, fs);
```







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
