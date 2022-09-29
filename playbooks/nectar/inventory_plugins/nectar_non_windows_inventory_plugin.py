#!/usr/bin/env python
# -*- encoding: utf-8 -*-

import os
import yaml
import sys


from ansible.plugins.inventory import BaseInventoryPlugin, Constructable, Cacheable
from ansible.errors import AnsibleParserError
from ansible.parsing.dataloader import DataLoader
from ansible.module_utils._text import to_bytes
from ceradmin_common.api.openstack_util import AppCredOpenstackUtil, UoANectarIPRegex

VM_USER_MANAGEMENT_BLOCKLIST = []
VM_USER_MANAGEMENT_BLOCKLIST_GROUP_NAME = 'group_management_blocklist'
WINDOWS_IMAGE_REGEX = 'UoA-Server201'
NON_WINDOWS_IMAGE_REGEX = f'^(?!.*{WINDOWS_IMAGE_REGEX})'
OS_TYPE="linux"

DOCUMENTATION = r'''
    name: nectar_non_windows_inventory_plugin
    plugin_type: inventory
    short_description: Returns Ansible inventory from nectar via openstack
    description: Returns Ansible inventory from nectar via openstack using application credentials
    options:
      plugin:
          description: Name of the plugin
          required: true
          choices: ['nectar_non_windows_inventory_plugin']
'''

class InventoryModule(BaseInventoryPlugin, Cacheable, Constructable):

    NAME = 'nectar_non_windows_inventory_plugin'

    def get_image_string(self, openstack_connection, server):
        suffix = ""
        image = openstack_connection.get_image_details(server['image']['id'])
        if image:
            try:
                suffix = image.name
            except AttributeError:
                suffix = image.description
        else:
            if 'virsh.guestinfo.os.pretty-name' in server['metadata']:
                # check if the OS has been set manually in an instance property
                suffix = server['metadata']['virsh.guestinfo.os.pretty-name']
        return '_'.join(suffix.split(' '))

    def get_platform_string(self, openstack_connection, server):
        metadata = server['metadata']
        return '_'.join(
            f"{metadata['os_family']}_{metadata['os_type']}_{metadata['os_version']}"\
            .split(' ')
         )
        # if not server['image']:
        #return f"{os_string}"
        #else:
        #    suffix = get_image_string(self, openstack_connection, server)
        #if suffix:
        #    return f"{os_string}_{suffix}"
        #else:
        #    return f"{os_string}"



    def verify_file(self, path):
        ''' return true/false if this is possibly a valid file for this plugin to consume '''
        valid = False
        if super(InventoryModule, self).verify_file(path):
            if path.endswith(('nectar_non_windows_inventory.yaml', 'nectar_non_windows_inventory.yml',)):
                valid = True
        return valid

    def get_vms(self, openstack_connection):
        """ access vsphere credentials via environment variables and query for vms"""
        search_options = {'status': 'ACTIVE', 'availability_zone': 'auckland', 'all_tenants': True}
        return openstack_connection.get_servers_by_os_type(os_type=OS_TYPE)


    def _populate(self):
        '''Return the hosts and groups'''
        try:
            config = AppCredOpenstackUtil.get_creds_from_environment()
        except Exception as e:
            sys.exit(str(e))
        openstack_connection = AppCredOpenstackUtil.from_config(config)
        self.nectar_non_windows_inventory = self.get_vms(openstack_connection)
        # Create the location, function and platform  groups
        platforms = []
        for server in self.nectar_non_windows_inventory:
            platform_string = self.get_platform_string(openstack_connection, server)
            if platform_string not in platforms:
                platforms.append(platform_string)
            server['platform'] = platform_string
        for platform in platforms:
            self.inventory.add_group(platform)
        # create group to contain blocklist for group management
        # self.inventory.add_group(VM_USER_MANAGEMENT_BLOCKLIST_GROUP_NAME)

        # Add the hosts to the groups
        for server in self.nectar_non_windows_inventory:
            hostname = server['ips'][0]
            self.inventory.add_host(host=hostname, group=server['platform'])
            self.inventory.set_variable(hostname, 'name', server['name'])

    def parse(self, inventory, loader, path, cache):
        # call base method to ensure properties are available for use with other helper methods

        super(InventoryModule, self).parse(inventory, loader, path, cache)
        self._read_config_data(path)
        try:
            self.plugin = self.get_option('plugin')
        except Exception as e:
            raise AnsibleParserError(f"all options are required {e}")
        self._populate()


def main():
    inv_module = InventoryModule()
    inv_module._populate()


if __name__ == '__main__':
    main()

# vim: fenc=utf-8: ft=python:sw=4:et:nu:fdm=indent:fdn=1:syn=python
