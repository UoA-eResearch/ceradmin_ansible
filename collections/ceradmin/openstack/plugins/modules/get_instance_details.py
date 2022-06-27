#!/usr/bin/python

from __future__ import (absolute_import, division, print_function)

import os
import novaclient.client as nova_client
import neutronclient.v2_0.client as neutron_client
from keystoneauth1 import identity, session
from ansible.module_utils.basic import AnsibleModule

__metaclass__ = type

DOCUMENTATION = r'''
---
module: get_instance_details
short_description: Return the first public IP and the project id
version_added: "1.0.0"
description: Return the first public IP and the project id

options:
    instance_id:
        description: ID of the Nectar instance
        required: true
        type: str
# Specify this value according to your collection
# in format of namespace.collection.doc_fragment_name
extends_documentation_fragment:
    - openstack.get_instance_details

author:
    - Martin Feller (@mondkaefer)
'''

EXAMPLES = r'''
# Pass in a message
- name: Test with a message
  openstack.get_instance_details:
    instance_id: 5dd81950-5a21-4095-830a-150d68499095

'''

RETURN = r'''
# These are examples of possible return values, and in general should use other names for return values.
details:
    description: Openstack server dict including floating ips of instance, or None
    type: dict
    returned: always
'''


# Return all IPv4 addresses of this instance
def get_server_ipv4s(server_dict):
    ips = []
    networks = server_dict['addresses'].values()
    for network in networks:
        ips.extend((address['addr'] for address in network if address['version'] == 4))
    return ips


# Return all active floating ip objects attached to this instance
def get_floating_ips(sess, server_dict):
    ips = []
    neutronc = neutron_client.Client(session=sess)
    fips = neutronc.list_floatingips(project_id=server_dict['tenant_id'])['floatingips']
    server_ipv4s = get_server_ipv4s(server_dict)
    for fip in fips:
        if fip['status'] == 'ACTIVE' and fip['fixed_ip_address'] in server_ipv4s:
            ips.append(fip)
    return ips


def run_module():
    module_args = dict(
        instance_id=dict(type='str', required=True)
    )

    result = dict(
        changed=False,
        details=None
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
    result['changed'] = False
    result['details'] = None
    auth = identity.v3.application_credential.ApplicationCredential(
             auth_url=os.environ['OS_AUTH_URL'],
             application_credential_id=os.environ['OS_APPLICATION_CREDENTIAL_ID'],
             application_credential_secret=os.environ['OS_APPLICATION_CREDENTIAL_SECRET'])
    sess = session.Session(auth=auth)
    novac = nova_client.Client(os_compute_api_version, session=sess)
    server = novac.servers.get(module.params['instance_id'])
    if server is not None:
        server_dict = server.to_dict()
        server_dict['floating_ips'] = get_floating_ips(sess, server_dict)
        result['details'] = server_dict

    module.exit_json(**result)


def main():
    run_module()


if __name__ == '__main__':
    main()
