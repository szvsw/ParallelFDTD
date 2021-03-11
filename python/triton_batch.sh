#!/bin/bash -l
#SBATCH -J parallelFDTD
#SBATCH -o parallelFDTD.out
#SBATCH -t 10:00:00
#SBATCH -p gpu
#SBATCH --gres=gpu:teslak80:8
#SBATCH --mem-per-cpu=128000

mkdir -p return

srun python testBench.py

mv ./*.log ./return/
mv ./*.hdf5 ./return/
mv ./*.out ./return/
