#!/usr/bin/python

from __future__ import (absolute_import, division, print_function)

import os
import keystoneclient.v3.client as keystone_client
from keystoneclient.exceptions import NotFound
from keystoneclient import utils
from keystoneauth1.identity import v3
from keystoneauth1 import session
from ansible.module_utils.basic import AnsibleModule

__metaclass__ = type

DOCUMENTATION = r'''
---
module: get_user_by_email
short_description: Look up user details by email address
version_added: "1.0.0"
description: Look up user details by email address

options:
    email:
        description: email of Nectar user
        required: true
        type: str
# Specify this value according to your collection
# in format of namespace.collection.doc_fragment_name
extends_documentation_fragment:
    - openstack.get_user_by_email

author:
    - Martin Feller (@mondkaefer)
'''

EXAMPLES = r'''
# Pass in a message
- name: Get user
  openstack.get_user_by_email
    email: m.feller@auckland.ac.nz

'''

RETURN = r'''
# These are examples of possible return values, and in general should use other names for return values.
details:
    description: Openstack user dict, or None
    type: dict
    returned: always
'''


def run_module():
    module_args = dict(
        email=dict(type='str', required=True)
    )

    result = dict(
        changed=False,
        user=None
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

    auth = v3.application_credential.ApplicationCredential(
             auth_url=os.environ['OS_AUTH_URL'],
             application_credential_id=os.environ['OS_APPLICATION_CREDENTIAL_ID'],
             application_credential_secret=os.environ['OS_APPLICATION_CREDENTIAL_SECRET'])
    keystone_c = keystone_client.Client(session=session.Session(auth=auth))
    try:
        result['user'] = utils.find_resource(keystone_c.users, module.params['email']).to_dict()
    except NotFound:
        module.fail_json(msg=f'No such user: {module.params["email"]}', **result)

    module.exit_json(**result)


def main():
    run_module()


if __name__ == '__main__':
    main()
