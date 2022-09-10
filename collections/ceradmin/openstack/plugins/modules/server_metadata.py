#!/usr/bin/python

from __future__ import (absolute_import, division, print_function)

import os
import novaclient.client as nova_client
from novaclient.exceptions import NotFound
from novaclient.v2.servers import ServerManager
from keystoneauth1 import session
from keystoneauth1.identity import v3
from ansible.module_utils.basic import AnsibleModule

__metaclass__ = type

DOCUMENTATION = r'''
---
module: set/remove server properties (aka metadata)
short_description: Set or remove server proper ties
version_added: "1.0.0"
description: Set or remove server proper ties

options:
    instance_id:
        description: ID of the Nectar server
        required: true
        type: str
    meta:
        description: A list of key value pairs that should be provided as a metadata
        required: true
        type: dict
    state:
        description: Should the resource be present or absent.
        choices: [present, absent]
        default: present
        type: str
# Specify this value according to your collection
# in format of namespace.collection.doc_fragment_name
extends_documentation_fragment:
    - ceradmin.openstack.server_metadata

author:
    - Martin Feller (@mondkaefer)
'''

EXAMPLES = r'''
# Pass in a message
- name: Test with a message
  ceradmin.openstack.server_metadata:
    instance_id: 5dd81950-5a21-4095-830a-150d68499095
    state: present
    meta:
      os: linux
'''

RETURN = r'''

'''


def _needs_update(server_metadata=None, metadata=None):
    if server_metadata is None:
        server_metadata = {}
    if metadata is None:
        metadata = {}
    return len(set(metadata.items()) - set(server_metadata.items())) != 0


def _get_keys_to_delete(server_metadata_keys=None, metadata_keys=None):
    if server_metadata_keys is None:
        server_metadata_keys = []
    if metadata_keys is None:
        metadata_keys = []
    return set(server_metadata_keys) & set(metadata_keys)


def run_module():
    module_args = dict(
        instance_id=dict(type='str', required=True),
        state=dict(choices=['absent', 'present'], required=True),
        meta=dict(type='dict', required=True)
    )

    result = dict(
        changed=False
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
    auth = v3.application_credential.ApplicationCredential(
               auth_url=os.environ['OS_AUTH_URL'],
               application_credential_id=os.environ['OS_APPLICATION_CREDENTIAL_ID'],
               application_credential_secret=os.environ['OS_APPLICATION_CREDENTIAL_SECRET'])
    sess = session.Session(auth=auth)
    nova_c = nova_client.Client(os_compute_api_version, session=sess)
    server_manager = ServerManager(nova_c)

    instance_id = module.params['instance_id']
    meta = module.params['meta']
    state = module.params['state']

    try:
        server = nova_c.servers.get(instance_id)
        if state == 'present':
            if _needs_update(server_metadata=server.metadata, metadata=meta):
                server_manager.set_meta(server, meta)
                result['changed'] = True
        elif state == 'absent':
            keys_to_delete = _get_keys_to_delete(server.metadata.keys(), meta.keys())
            if len(keys_to_delete) > 0:
                server_manager.delete_meta(server, keys_to_delete)
                result['changed'] = True
    except NotFound:
        module.fail_json(msg=f'No such server: {instance_id}', **result)

    module.exit_json(**result)


def main():
    run_module()


if __name__ == '__main__':
    main()
