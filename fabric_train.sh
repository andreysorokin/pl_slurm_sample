#!/bin/bash
# Evertything can be overridden
#SBATCH --output=/shared/logs/train.%j.out
#SBATCH --error=/shared/logs/train.%j.err
#SBATCH --nodes=2               # This needs to match the param below
#SBATCH --ntasks-per-node=1     # This needs to match the param below
#SBATCH --mem=0
#SBATCH --time=0-12:00:00

# Please, update GLOO socket accordingly
export GLOO_SOCKET_IFNAME=enp0s8
source /home/vagrant/venv/bin/activate
srun python /vagrant/fabric_slurm_smaller.py --num_nodes=2 --devices=1