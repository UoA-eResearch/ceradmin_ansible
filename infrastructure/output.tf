output "awx_private_key" {
  value     = openstack_compute_keypair_v2.awx_keypair.private_key
  sensitive = true
}

output "awx_instance_all_metadata" {
  value = openstack_compute_instance_v2.awx_instance.all_metadata
}

output "awx_instance_public_ip_address_1" {
  value     = openstack_compute_instance_v2.awx_instance.network.0.fixed_ip_v4
}

output "awx_instance_public_ip_address_2" {
  value     = openstack_compute_instance_v2.awx_instance.network.1.fixed_ip_v4
}
