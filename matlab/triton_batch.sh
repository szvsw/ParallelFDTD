#!/bin/bash -l
#SBATCH --time=00:10:00
#SBATCH -p gpu
#SBATCH -o LOG_FILE.out
#SBATCH --gres=gpu:teslap100:1

module load gcc/6.3.0 cuda matlab 

# Run the job

srun matlab -nojvm -nosplash -batch "testBench()"
