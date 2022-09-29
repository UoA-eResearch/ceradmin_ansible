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
OS_TYPE="windows"

DOCUMENTATION = r'''
    name: nectar_windows_inventory_plugin
    plugin_type: inventory
    short_description: Returns Ansible inventory from nectar via openstack
    description: Returns Ansible inventory from nectar via openstack using application credentials
    options:
      plugin:
          description: Name of the plugin
          required: true
          choices: ['nectar_windows_inventory_plugin']
'''

class InventoryModule(BaseInventoryPlugin, Cacheable, Constructable):

    NAME = 'nectar_windows_inventory_plugin'

    def get_platform_string(self, openstack_connection, data):
        image = openstack_connection.get_image_details(data['image']['id'])

        try:
            return image.name
        except AttributeError:
            return image.description

    def verify_file(self, path):
        ''' return true/false if this is possibly a valid file for this plugin to consume '''
        valid = False
        if super(InventoryModule, self).verify_file(path):
            if path.endswith(('nectar_windows_inventory.yaml', 'nectar_windows_inventory.yml',)):
                valid = True
        return valid

    def get_vms(self, openstack_session):
        """ access vsphere credentials via environment variables and query for vms"""
        search_options = {'status': 'ACTIVE', 'availability_zone': 'auckland', 'all_tenants': True}
        return openstack_session.get_servers_by_os_type(os_type=OS_TYPE)


    def _populate(self):
        '''Return the hosts and groups'''
        try:
            config = AppCredOpenstackUtil.get_creds_from_environment()
        except Exception as e:
            sys.exit(str(e))
        openstack_session = AppCredOpenstackUtil.from_config(config)
        self.nectar_windows_inventory = self.get_vms(openstack_session)
        # Create the location, function and platform  groups
        platforms = []
        for data in self.nectar_windows_inventory:
            platform_string = self.get_platform_string(openstack_session, data)
            if platform_string not in platforms:
                platforms.append(platform_string)
            data['platform'] = platform_string
        for platform in platforms:
            self.inventory.add_group(platform)
        # create group to contain blocklist for group management
        # self.inventory.add_group(VM_USER_MANAGEMENT_BLOCKLIST_GROUP_NAME)

        # Add the hosts to the groups
        for data in self.nectar_windows_inventory:
            hostname = data['ips'][0]
            self.inventory.add_host(host=hostname, group=data['platform'])
            self.inventory.set_variable(hostname, 'name', data['name'])

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
