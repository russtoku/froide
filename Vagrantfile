# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.require_version ">= 1.7.2"

Vagrant.configure(2) do |config|

  config.ssh.insert_key = true

  config.vm.box = "ubuntu/vivid64"
  config.vm.box_check_update = false
  config.vm.define "froide_vm"

  # config.vm.hostname = 'froide.local'

  config.vm.network "private_network", ip: "192.168.51.51"
  config.vm.network "forwarded_port", guest: 8000, host: 50051, auto_correct: true

  config.vm.provider "virtualbox" do |vm|
    vm.name = "froide_vm"
  end
end
