# How to deploy your script in the AWS

# Create an instance

## Install packages

```bash
sudo yum update
sudo yum install git 
sudo yum install tmux
sudo yum install wget
```

## Install Python/Conda

https://docs.anaconda.com/miniconda/#quick-command-line-install

```bash
conda create -n trading python=3.11
conda activate trading
```

## Install Scheduler

```bash
   32  sudo yum install cronie -y
   33  sudo systemctl enable crond.service
   34  sudo systemctl start crond.service
   35  sudo systemctl status crond | grep Active
```

