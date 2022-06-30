#!/usr/bin/python

from __future__ import (absolute_import, division, print_function)

import re
import os
import novaclient.client as nova_client
import neutronclient.v2_0.client as neutron_client
from keystoneauth1.identity import v3
from keystoneauth1 import session
from ansible.module_utils.basic import AnsibleModule

__metaclass__ = type

DOCUMENTATION = r'''
---
module: get_servers
short_description: Return list of servers
version_added: "1.0.0"
description: Return list of Linux servers

options:
    search_opts:
        description: search options to filter the list of servers by
        required: true
        type: dict
    metadata_filter:
        description: server metadata fields to filter the list of servers by
        required: false
        type: dict
    ip_regex:
        description: IP regex to filter the list of servers by
        required: false
        type: str
    
# Specify this value according to your collection
# in format of namespace.collection.doc_fragment_name
extends_documentation_fragment:
    - ceradmin.openstack.get_servers

author:
    - Martin Feller (@mondkaefer)
'''

EXAMPLES = r'''
# Pass in a message
- name: Test with a message
  ceradmin.openstack.get_servers:
    search_opts: { 'all_tenants': True, 'availability_zone': 'auckland' }
    metadata_filter: { 'os_type': 'linux' }
    ip_regex: '130\\.216\\..*'
'''

RETURN = r'''
# These are examples of possible return values, and in general should use other names for return values.
details:
    description: List of Openstack server dicts including floating ips
    type: list
    returned: always
'''


# Return all IPv4 addresses of this server
def get_server_ipv4s(server_dict):
    ips = []
    networks = server_dict['addresses'].values()
    for network in networks:
        ips.extend((address['addr'] for address in network if address['version'] == 4))
    return ips


# Return all active floating ip objects attached to this server
def get_floating_ips(sess, server_dict):
    ips = []
    neutron_c = neutron_client.Client(session=sess)
    fips = neutron_c.list_floatingips(project_id=server_dict['tenant_id'])['floatingips']
    server_ipv4s = get_server_ipv4s(server_dict)
    for fip in fips:
        if fip['status'] == 'ACTIVE' and fip['fixed_ip_address'] in server_ipv4s:
            ips.append(fip)
    return ips


def has_public_ipv4s(server_dict):
    ipv4s = get_server_ipv4s(server_dict)
    ipv4s.extend((fip['floating_ip_address'] for fip in server_dict['floating_ips']))
    found = False
    for ipv4 in ipv4s:
        if re.match('^130\\.216\\..*', ipv4):
            found = True
    return found


def filter_by_metadata(server_dicts: list, metadata_filter: dict):
    tmp = []
    if metadata_filter is None:
        tmp = server_dicts
    else:
        for server_dict in server_dicts:
            metadata = server_dict['metadata']
            for key in metadata_filter.keys():
                if key in metadata and metadata[key] == metadata_filter[key]:
                    tmp.append(server_dict)
    return tmp


def filter_by_ip_regex(server_dicts: list, ip_regex: str):
    tmp = []
    if ip_regex is None:
        tmp.extend(server_dicts)
    else:
        for server_dict in server_dicts:
            ipv4s = get_server_ipv4s(server_dict)
            ipv4s.extend(fip['floating_ip_address'] for fip in server_dict['floating_ips'])
            for ipv4 in ipv4s:
                if re.match(ip_regex, ipv4):
                    tmp.append(server_dict)
                    break
    return tmp


def run_module():
    module_args = dict(
        search_opts=dict(type='dict', required=True),
        metadata_filter=dict(type='dict', required=False),
        ip_regex=dict(type='str', required=False)
    )

    result = dict(
        changed=False,
        servers=[]
    )

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )

    if module.check_mode:
        module.exit_json(**result)

    # Verify required environment variables are defined
    for x in ['OS_AUTH_URL', 'OS_APPLICATION_CREDENTIAL_ID', 'OS_APPLICATION_CREDENTIAL_SECRET']:
        if x not in os.environ:
            module.fail_json(msg='%s is not set as environment variable' % x, **result)

    os_compute_api_version: float = 2.83
    result['servers'] = []
    auth = v3.application_credential.ApplicationCredential(
             auth_url=os.environ['OS_AUTH_URL'],
             application_credential_id=os.environ['OS_APPLICATION_CREDENTIAL_ID'],
             application_credential_secret=os.environ['OS_APPLICATION_CREDENTIAL_SECRET'])
    sess = session.Session(auth=auth)
    nova_c = nova_client.Client(os_compute_api_version, session=sess)
    servers = nova_c.servers.list(search_opts=module.params['search_opts'])
    server_dicts = []
    for server in servers:
        tmp = server.to_dict()
        tmp['floating_ips'] = get_floating_ips(sess, tmp)
        server_dicts.append(tmp)
    server_dicts = filter_by_metadata(server_dicts, module.params['metadata_filter'])
    server_dicts = filter_by_ip_regex(server_dicts, module.params['ip_regex'])
    result['servers'].extend(server_dicts)

    module.exit_json(**result)


def main():
    run_module()


if __name__ == '__main__':
    main()
