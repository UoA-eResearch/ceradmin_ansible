# Define required providers
terraform {
  required_version = ">= 0.14.0"
  required_providers {
    openstack = {
      source  = "terraform-provider-openstack/openstack"
      version = "~> 1.53.0"
    }
  }
  cloud {
    organization = "uoa_cer"

    workspaces {
      name = "awx_dev"
    }
  }
}

# Configure the OpenStack Provider
provider "openstack" {
  auth_url                      = var.os_auth_url
  application_credential_id     = var.os_application_credential_id
  application_credential_secret = var.os_application_credential_secret
  tenant_id                     = var.os_project_id
  tenant_name                   = var.os_project_name
  region                        = var.os_region
  enable_logging                = true
}

resource "openstack_compute_keypair_v2" "awx_keypair" {
  # Get the key from tfstate after deployment
  name = "tlau020_awx_keypair"
}

resource "openstack_networking_secgroup_v2" "awx_secgroup" {
  name        = "tlau020_awx_secgroup"
  description = "Security group for the AWX instance"
  tenant_id   = var.os_project_id
}

variable "ip_address_ranges" {
  type    = list(string)
  default = ["130.216.0.0/16", "172.16.0.0/12", "192.168.0.0/16", "10.0.0.0/8"]
}

resource "openstack_networking_secgroup_rule_v2" "awx_secgroup_rules_ssh" {
  count = length(var.ip_address_ranges)

  direction         = "ingress"
  ethertype         = "IPv4"
  protocol          = "tcp"
  port_range_min    = 22
  port_range_max    = 22
  remote_ip_prefix  = var.ip_address_ranges[count.index]
  security_group_id = openstack_networking_secgroup_v2.awx_secgroup.id
  tenant_id         = var.os_project_id
}

resource "openstack_networking_secgroup_rule_v2" "awx_secgroup_rules_https" {
  count = length(var.ip_address_ranges)

  direction         = "ingress"
  ethertype         = "IPv4"
  protocol          = "tcp"
  port_range_min    = 443
  port_range_max    = 443
  remote_ip_prefix  = var.ip_address_ranges[count.index]
  security_group_id = openstack_networking_secgroup_v2.awx_secgroup.id
  tenant_id         = var.os_project_id
}

resource "openstack_compute_instance_v2" "awx_instance" {
  name              = "tlau020_awx_instance"
  image_id          = var.os_image_id
  flavor_id         = var.os_flavor_id
  key_pair          = openstack_compute_keypair_v2.awx_keypair.name
  availability_zone = var.os_availability_zone

  security_groups = [
    "default",
    # Documentation states that the name is needed, but the ID is the only property that works
    openstack_networking_secgroup_v2.awx_secgroup.id
  ]
}

locals {
  # Instances have an "auckland-public" and "auckland-public-data" network
  # The "auckland-public" network is the one we want, so find the index of it in the network block
  network_index = index(openstack_compute_instance_v2.awx_instance.network[*].name, "auckland-public")
}

resource "openstack_dns_recordset_v2" "awx_recordset" {
  zone_id = var.os_dns_zone
  name    = "awx.auckland-cer.cloud.edu.au."
  ttl     = 300
  type    = "A"
  records = [
    openstack_compute_instance_v2.awx_instance.network[local.network_index].fixed_ip_v4
  ]
}
