# Setup

1. Updarte `COMPUTE NODES` section of slurm.conf if required
2. Install vagrant
3. Install plugins: `vagrant plugin install vagrant-hostmanager`
4. `vagrant up`


## Notes on the setup

Configuration can be generated via /usr/share/doc/slurmctld/slurm-wlm-configurator.html

If node worker2 is down, then `scontrol update nodename=worker2 state=resume`

One of the possibilities that munge service will become out of sync on controller node, then:

    systemctl restart munge

The number of nodes or number of devices per node is configured incorrectly: There are two parameters in the SLURM submission script that determine how many processes will run your training, the #SBATCH --nodes=X setting and #SBATCH --ntasks-per-node=Y settings. The numbers there need to match what is configured in your Trainer in the code: Trainer(num_nodes=X, devices=Y)

## Validate the setup

Run on controller node:

    sbatch --nodes=2 test.sh

# Running actual training

## Validating for a single node

### on a single worker 1 node

    sbatch --nodelist=worker1 /vagrant/fabric_train.sh

### for every node in a cluster:

Update params inside fabric_train, then...

    sbatch /vagrant/fabric_train.sh

# Destroy

    vagrant destroy -f    
