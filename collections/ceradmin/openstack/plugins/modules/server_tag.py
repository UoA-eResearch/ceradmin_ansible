#!/usr/bin/python

from __future__ import (absolute_import, division, print_function)

import os
import novaclient.client as nova_client
from novaclient.exceptions import NotFound
from keystoneauth1 import session
from keystoneauth1.identity import v3
from ansible.module_utils.basic import AnsibleModule

__metaclass__ = type

DOCUMENTATION = r'''
---
module: server_tag
short_description: Set/remove tags on/from a server
version_added: "1.0.0"
description: Set/remove tags on/from a server

options:
    instance_id:
        description: ID of the Nectar server
        required: true
        type: str
    state:
        description: Should the resource be present or absent.
        choices: [present, absent]
        default: present
        type: str
    tags:
        description: tags to be added or removed
        required: true
        type: list
# Specify this value according to your collection
# in format of namespace.collection.doc_fragment_name
extends_documentation_fragment:
    - ceradmin.openstack.server_tag

author:
    - Martin Feller (@mondkaefer)
'''

EXAMPLES = r'''
# Pass in a message
- name: Test with a message
  ceradmin.openstack.server_tag:
    instance_id: 5dd81950-5a21-4095-830a-150d68499095
    state: present
    tags:
      - test1
      - test2
'''

RETURN = r'''

'''


def run_module():
    module_args = dict(
        instance_id=dict(type='str', required=True),
        state=dict(choices=['absent', 'present'], required=True),
        tags=dict(type='list', required=True)
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
    instance_id = module.params['instance_id']
    state = module.params['state']
    tags = module.params['tags']

    try:
        server = nova_c.servers.get(instance_id)
        server_tags = server.tag_list()
        if state == 'present':
            for tag in tags:
                if tag not in server_tags:
                    server.add_tag(tag)
                    result['changed'] = True
        elif state == 'absent':
            for tag in tags:
                if tag in server_tags:
                    server.delete_tag(tag)
                    result['changed'] = True
    except NotFound:
        module.fail_json(msg=f'No such server: {instance_id}', **result)

    module.exit_json(**result)


def main():
    run_module()


if __name__ == '__main__':
    main()
