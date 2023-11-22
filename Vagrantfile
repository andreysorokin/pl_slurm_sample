# -*- mode: ruby -*-
# vi: set ft=ruby :


$common_init = <<-SCRIPT
sudo apt-get update
sudo apt-get install -y munge slurm-wlm

# Start Munge service
if [[ $(hostname) == "controller" ]]; then
  # Create Munge key
  sudo mungekey -c -f -v
  sudo cp -f /etc/munge/munge.key /shared/.
else
  sudo cp -f /shared/munge.key /etc/munge/munge.key
fi

sudo chown munge: /etc/munge/munge.key
sudo chmod 400 /etc/munge/munge.key

sudo systemctl enable munge
sudo systemctl start munge

# Configure SLURM
sudo cp -f /vagrant/slurm.conf /etc/slurm/slurm.conf
sudo chmod 400 /etc/slurm/slurm.conf
sudo chown root /etc/slurm/slurm.conf

# Start SLURM services
if [[ $(hostname) == "controller" ]]; then
  sudo systemctl enable slurmctld
  sudo systemctl start slurmctld
else

  cat << CGROUP | sudo tee -a /etc/slurm/cgroup.conf 
CgroupAutomount=yes
ConstrainCores=no
ConstrainRAMSpace=no
CGROUP

  sudo systemctl enable slurmd
  sudo systemctl start slurmd
fi
SCRIPT

$create_swap = <<-SCRIPT

# size of swapfile in megabytes
swapsize=8000

# does the swap file already exist?
grep -q "swapfile" /etc/fstab

# if not then create it
if [ $? -ne 0 ]; then
  echo 'swapfile not found. Adding swapfile.'
  fallocate -l ${swapsize}M /swapfile
  chmod 600 /swapfile
  mkswap /swapfile
  swapon /swapfile
  echo '/swapfile none swap defaults 0 0' >> /etc/fstab
else
  echo 'swapfile found. No changes made.'
fi

SCRIPT

$torch_init = <<-SCRIPT
sudo apt-get update
sudo apt install -y python3.10-venv
cd /home/vagrant

python3 -m venv venv
source venv/bin/activate
pip install lightning transformers lightning-transformers torch jsonargparse dataclasses

SCRIPT

workers_count = 2

Vagrant.configure("2") do |config|
  # Global settings
  config.vm.box = "ubuntu/jammy64"
  config.vm.synced_folder "./shared", "/shared"

  config.hostmanager.enabled = true
  config.hostmanager.manage_host = false
  config.hostmanager.manage_guest = true
  config.hostmanager.include_offline = true
  config.hostmanager.ignore_private_ip = false

  # Controller node configuration
  config.vm.define "controller" do |controller|
    controller.vm.hostname = "controller"
    controller.vm.network "private_network", ip: "10.10.10.2", virtualbox__intnet: true
    controller.vm.provision "shell", inline: $common_init

    # Some cleanup routines
    controller.trigger.before :destroy do |trigger|
      trigger.run_remote = {inline:  "rm -f /shared/.controller_provisioned && rm -f /shared/munge.key"}
    end
  end

  # Worker node configuraion
  (1..workers_count).each do |i|
    config.vm.define "worker#{i}" do |worker|
      worker.vm.hostname = "worker#{i}"
      worker.vm.network "private_network", ip: "10.10.10.#{i + 2}", virtualbox__intnet: true
      worker.vm.provision "shell", inline: $create_swap
      worker.vm.provision "shell", inline: $common_init
      worker.vm.provision "shell", inline: $torch_init
      
      worker.vm.provider "virtualbox" do |v|
        v.memory = 8192
        v.cpus = 2
      end
      
    end

  end

end

