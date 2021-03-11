# -*- coding: utf-8 -*-
"""
Created on Thu Aug  7 10:20:05 2014

@author: Jukka Saarelma

"""

# Before running this you need to activate the anaconda environment
#  conda activate PFDTD
# and install matplotlib and h5py
#  conda install -c conda-forge matplotlib h5py

import numpy as np
import matplotlib.pyplot as plt
import json
import h5py

# Load the FDTD library
import pyParallelFDTD as pf

###############################################################################
# Assign simulation parameters
###############################################################################

# Which update to use is device dependent. SRL forward is most probably
# the most efficient choice. SRL forward sliced might be faster with some
# devices, and when using double precision. SRL centered is a bit of a
# curiosity and definitely has the worst computational performance of the choices.
#
# The downside of SRL FDTD scheme which is used here, is the dispersion
# error. The error is well known, and an interested reader should get
# familiar with following publications [3][6]. A 10 time oversampling is
# commonly used with the SRL scheme that results in ~2 % dispersion error.
# An example, if a 1000 Hz band limit is to be achieved, the sampling
# frequency of the domain should be 10,000 Hz.

# Another downside of SRL scheme is that the simulation domain is a so
# called staircase approximation. This can lead to a slight deviation of the
# modes of the space. An interested reader can see [1].

update_type = 0 # 0: SRL forward, 1: SRL sliced, 2: SRL centred
num_steps = 2000
fs = 100000

# Force the App to use given number of
# partitions, namely the number of devices.
# Visualization will override this and use
# only one device.
num_partition = 1

# The selection of precision and the type of source has an effect on the stability
# of the simulation [2]. As a guideline, double precision should be used
# for simulation of impulse responses. For visualization purposes, single precision
# is the only precision supported, and suffices for the purpose of
# visualization of early reflections and scattering.
double_precision = False


src_type = 0             # 0: Hard, 1: Soft, 2: Transparent
input_type = 1           # 0: Delta, 1: Gaussian, 2: Sine, 3: Given data
input_data_idx = 0       # In the case of arbitrary input data, the
                         # input data vector index has to be given
                         # for each source. The input data is loaded
                         # later in this script.


# Source setup. Sources have to be in shape of N X 6, where N is the number
# of sources
src = [0.5, 0.5, 0.5]

# Receivers, shape N X 3
rec = [[0.6, 0.6, 0.6],
       [0.4, 0.4, 0.4]]

# Choose wether to run visualizations or captures
visualization = False
captures = True

###############################################################################
# Load the model from JSON format
###############################################################################

# A JSON importer is used in this case, any format which is possible
# to import a geometry to the workspace can be used.
# The end product after parsing should be a list of vertices coordinates
# (in meters), and a list of triangle indices defining the geometry.
# Triangle indices have to start from 0.

fp = "./Data/box.json"
file_stream = open(fp)
m = json.load(file_stream)
file_stream.close()

###############################################################################
# Parse the geometry from the data
###############################################################################
vertices = np.reshape(m["vertices"], (int(np.size(m["vertices"])/3), 3))
indices = np.reshape(m["indices"], (int(np.size(m["indices"])/3), 3))

###############################################################################
# Assign reflection coefficients to different layers
###############################################################################

# First, get the layer list and enumerate the surfaces on each layer
layer_list = m["layers_of_triangles"]
layer_names = m["layer_names"]
layers = {}

for k in range(0, len(layer_names)):
  layer_indices = [i for i, j in enumerate(layer_list) if j == layer_names[k]]
  layers[layer_names[k]] = layer_indices

# The materials are given as a [N x 20] matrix where
# N is the number of polygon in the geometry
num_triangles = int(np.size(indices)/3)
num_coef = 20 # Default number of coefficients

# 20 values is somewhat arbitrary
# number, which rationale is to accomodate 2 variables per 10 octave bands
# to be used in the calculation in future work.
# Now only one variable is used, which is an admittance value

# Functions to map reflection and absorbtion rates to admittance values
def reflection2Admittance(R):
    return (1.0-R)/(1.0+R)

def absorption2Admittance(alpha):
    return reflection2Admittance(np.sqrt(1.0-alpha))

# First set an uniform material
R_glob = 0.99
materials = np.ones((num_triangles, num_coef))*reflection2Admittance(R_glob)

# Grab the triangle indices of the given layer from the 'layers' list.
# Assign a material to those triangles in the material list
materials[layers['walls'], :] = reflection2Admittance(R_glob)
materials[layers['ceiling'], :] = reflection2Admittance(R_glob)
materials[layers['floor'], :] = reflection2Admittance(R_glob)

###############################################################################
# Assign image captures to the simulations
###############################################################################

# Captures of slices of the domain in certain time steps
# size is Nx3, where N is the number of captures and the
# three parameters given are [slice, step, orientation]

slice_n = 60
step = 100
orientation = 1
capture = [slice_n, step, orientation]

###############################################################################
# Initialize and run the FDTD solver
###############################################################################
app = pf.App()
app.initializeDevices()
app.initializeGeometryPy(indices.flatten().tolist(), vertices.flatten().tolist())
app.setUpdateType(update_type)
app.setNumSteps(int(num_steps))
app.setSpatialFs(fs)
app.setDouble(double_precision)
app.forcePartitionTo(num_partition)
app.addSurfaceMaterials(materials.flatten().tolist(), num_triangles, num_coef)

app.addSource(src[0], src[1], src[2], src_type, input_type, input_data_idx)

for i in range(0, np.shape(rec)[0]):
  app.addReceiver(rec[i][0],rec[i][1],rec[i][2])

if visualization:
    # The visualization is run on a separate worker for stable OpenGL.
    # This is a Windows spesific precaution, on unix based systems the
    # matlabpool commands can be safely commented out.
    app.runVisualization()

elif captures:
    app.addSliceToCapture(capture[0], capture[1], capture[2])
    app.runCapture()

else:
    app.runSimulation()

###############################################################################
# Parse the return values
###############################################################################

ret = []
for i in range(0, np.shape(rec)[0]):
  if double_precision:
    ret.append(np.array(app.getResponseDouble(i)))
  else:
    ret.append(np.array(app.getResponse(i)))

# Cast to Numpy array for convenient slicing
ret = np.transpose(np.array(ret))
plt.plot(ret)


# Save some important results in the hdf5 format
fp_out = 'box'+"_"+str(int(np.round(fs)))+'.hdf5'
f = h5py.File(fp_out, 'w')
f.create_dataset('ret', data=ret)
f['src'] = src
f['rec'] = rec
f['dx'] = dx
f['dt'] = dt
f['fs'] = fs
f.close()

# Remember to close and delete the solver after you're done!
app.close()
del app



###############################################################################
# References
###############################################################################

# [1] Bilbao, S. Modeling of complex geometries and boundary conditions
#     in finite difference/finite volume time domain room acoustics simulation.
#     Audio, Speech, and Language Processing, IEEE Transactions on 21, 7
#     (2013), 1524-1533.

# [2] Botts, J., and Savioja, L. "Effects of sources on time-domain Finite
#     difference models." The Journal of the Acoustical Society of America 136,
#     1 (2014), 242-247.

# [3] Kowalczyk, K. "Boundary and medium modelling using compact finite
#     diffrence schemes in simulation of room acoustics for audio and archi-
#     tectural design applications." PhD thesis, School of Electorincs, Electrical
#     Engineering and Computer Science, Queen's University Belfast, 2008.

# [4] Luizard, P., Otani, M., Botts, J., Savioja, L., and Katz, B. F.
#     "Comparison of sound field measurements and predictions in coupled
#     volumes between numerical methods and scale model measurements." In
#     Proceedings of Meetings on Acoustics (2013), vol. 19, Acoustical Society
#     of America, p. 015114.

# [5] Sheaffer, J., Walstijn, M., and Fazenda, B. A "Physically constrained
#     source model for fdtd acoustic simulation." In Proc. of the
#     15th Int. Conference on Digital Audio Effects (DAFx-12) (2012).

# [6] Trefethen, L. N. "Group velocity in finite difference schemes." SIAM review 24, 2
#    (1982), 113-136.
